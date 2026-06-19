import os
import cv2
import numpy as np
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.utils import class_weight
from tensorflow.keras import layers, models
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.applications.mobilenet_v2 import preprocess_input
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau
from src.progress_state import progress

IMG_SIZE = 160
DATA_PATH = "data"
LIMIT = 4000

def load_data(data_dir, limit=4000):
    images, labels = [], []

    categories = ["no", "yes"]

    for label, category in enumerate(categories):
        path = os.path.join(data_dir, category)

        if not os.path.exists(path):
            print(f"Folder not found: {path}")
            continue

        count = 0
        print(f"\nLoading {category}...")

        for img in os.listdir(path):
            if count >= limit // 2:
                break

            img_path = os.path.join(path, img)

            try:
                image = cv2.imread(img_path)

                if image is None:
                    continue

                image = cv2.resize(image, (IMG_SIZE, IMG_SIZE))
                image = image / 255.0

                images.append(image)
                labels.append(label)
                count += 1

            except Exception as e:
                print(f"⚠️ Skipped: {img_path}")

        print(f" {category}: {count} images")

    if len(images) == 0:
        raise ValueError("No images loaded. Check dataset path.")

    return np.array(images), np.array(labels)

X, y = load_data(DATA_PATH, LIMIT)

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

weights = class_weight.compute_class_weight(
    class_weight='balanced',
    classes=np.unique(y),
    y=y
)
class_weights = dict(enumerate(weights))
print("Class Weights:", class_weights)

datagen = ImageDataGenerator(
    rotation_range=25,
    zoom_range=0.2,
    width_shift_range=0.1,
    height_shift_range=0.1,
    horizontal_flip=True
)

base_model = MobileNetV2(
    input_shape=(IMG_SIZE, IMG_SIZE, 3),
    include_top=False,
    weights="imagenet"
)

base_model.trainable = False

x = base_model.output
x = layers.GlobalAveragePooling2D()(x)
x = layers.BatchNormalization()(x)
x = layers.Dense(256, activation='relu')(x)
x = layers.Dropout(0.5)(x)

output = layers.Dense(1, activation='sigmoid')(x)

model = models.Model(inputs=base_model.input, outputs=output)

model.compile(
    optimizer=Adam(learning_rate=0.0003),
    loss='binary_crossentropy',
    metrics=['accuracy']
)

early_stop = EarlyStopping(patience=5, restore_best_weights=True)
reduce_lr = ReduceLROnPlateau(patience=3, factor=0.3)

print("\n Phase 1 Training...")
model.fit(
    datagen.flow(X_train, y_train, batch_size=32),
    epochs=15,
    validation_data=(X_test, y_test),
    class_weight=class_weights,
    callbacks=[early_stop, reduce_lr]
)

print("\n Fine-tuning...")

base_model.trainable = True
for layer in base_model.layers[:-50]:
    layer.trainable = False

model.compile(
    optimizer=Adam(learning_rate=0.00005),
    loss='binary_crossentropy',
    metrics=['accuracy']
)

history = model.fit(
    datagen.flow(X_train, y_train, batch_size=32),
    epochs=20,
    validation_data=(X_test, y_test),
    class_weight=class_weights,
    callbacks=[early_stop, reduce_lr]
)

loss, acc = model.evaluate(X_test, y_test)
print(f"\n Final Accuracy: {acc * 100:.2f}%")

os.makedirs("model", exist_ok=True)
model.save("model/brain_tumor_best.h5")

print("\n Model saved!")