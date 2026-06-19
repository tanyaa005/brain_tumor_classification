import numpy as np
import cv2
from functools import wraps
from flask import jsonify
# from tensorflow.keras.applications.mobilenet_v2 import preprocess_input
from flask_jwt_extended import (
    create_access_token,
    verify_jwt_in_request,
    get_jwt_identity,
    unset_jwt_cookies,
    jwt_required as jwt_required_original
)

IMG_SIZE = 160

def preprocess_image(file):
    file_bytes = np.frombuffer(file.read(), np.uint8)
    image = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)

    image = cv2.resize(image, (IMG_SIZE, IMG_SIZE))
    image = image / 255.0
    # image = preprocess_input(image)

    image = np.expand_dims(image, axis=0)
    return image

def create_clients(X, y, num_clients=2):
    data_size = len(X) // num_clients
    clients = []

    for i in range(num_clients):
        start = i * data_size
        end = (i + 1) * data_size
        clients.append((X[start:end], y[start:end]))

    return clients


# def generate_token(user):
#     return create_access_token(identity=user.id,details=user)
def generate_token(user):
    user_id = user['id'] if isinstance(user, dict) else user.id
    if isinstance(user, dict):
        user_id = str(user.get('id'))
        user_details = user
    else:
        user_id = str(user.id)
        user_details = user.to_dict() if hasattr(user, 'to_dict') else vars(user)
        
    return create_access_token(
        identity=user_id,  # This must be a string
        additional_claims={
            "user_details": user_details
        }
    )

def logout_response():
    response = jsonify({"message": "Logged out successfully"})
    unset_jwt_cookies(response)
    return response

def jwt_required(fn=None, optional=False, fresh=False, refresh=False):
    """
    Custom JWT decorator that handles errors consistently
    Can be used as @jwt_required or @jwt_required()
    """
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            try:
                verify_jwt_in_request()
                return fn(*args, **kwargs)
            except Exception as e:
                return jsonify({
                    "status": "error",
                    "message": str(e) or "Invalid or expired token"
                }), 401
        return decorator
    
    # Handle both @jwt_required and @jwt_required() usage
    if fn:
        return wrapper(fn)
    return wrapper
