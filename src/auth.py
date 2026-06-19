from flask import Blueprint, render_template, request, redirect, url_for, session, current_app
# from werkzeug.security import generate_password_hash, check_password_hash
from src.database import mysql
from MySQLdb.cursors import DictCursor
import jwt
import datetime

auth = Blueprint('auth', __name__)

@auth.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        data = request.get_json()
        username = data.get('username')
        email = data.get('email') or None
        password = data.get('password').strip()

        if not username or not password:
            return {"success": False, "message": "All fields required"}

        bcrypt = current_app.config['BCRYPT']
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

        try:
            cur = mysql.connection.cursor()
            cur.execute(
                "INSERT INTO auth_users(username, email, password) VALUES(%s, %s, %s)",
                (username, email, hashed_password)
            )
            mysql.connection.commit()
            return {"success": True, "message": "Registration successful"}

        except Exception as e:
            return {"success": False, "message": str(e)}


        finally:
            cur.close()

    return render_template('register.html')

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = request.get_json()

        username = data.get('username')
        password = data.get('password').strip()
        bcrypt = current_app.config['BCRYPT']

        if not username or not password:
            return {"success": False, "message": "All fields required"}

        try:
            cur = mysql.connection.cursor(DictCursor)
            cur.execute(
                "SELECT * FROM auth_users WHERE username=%s",
                (username,)
            )
            user = cur.fetchone()
            cur.close()

            if user:
                if user['status'] != 1:
                    return {"success": False, "message": "Account is inactive"}

                if  bcrypt.check_password_hash(user['password'], password):
                    session['user'] = user['username']
                    session['role'] = user['role']
                    token = jwt.encode({
                        'user': user['username'],
                        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=2)
                        }, current_app.secret_key, algorithm="HS256")

                    return {
                        "success": True, 
                        "message": "Login successful",
                        "data": {
                            "access_token": token
                            }
                        }
                else:
                    return {"success": True, "message": "Login invalid"}
            else:
                return {"success": False, "message": "Acc not found"}

        except Exception as e:
            print("DB ERROR:", e)
            return {"success": False, "message": "Database error"}

    return render_template('login.html')

@auth.route('/logout', methods=['POST'])
def logout():
    session.pop('user', None)

    return {
        "success": True,
        "message": "Logged out successfully"
    }

@auth.route('/users')
def users_list():
    if 'user' not in session:
        return redirect(url_for('auth.login'))

    cur = mysql.connection.cursor(DictCursor)
    cur.execute("SELECT id, username, email, status FROM auth_users")
    users = cur.fetchall()
    cur.close()

    return render_template('users.html', users=users)

@auth.route('/users/edit/<int:id>', methods=['GET', 'POST'])
def edit_user(id):
    if 'user' not in session:
        return redirect(url_for('auth.login'))

    cur = mysql.connection.cursor(DictCursor)

    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        status = request.form.get('status')

        cur.execute(
            "UPDATE auth_users SET username=%s, email=%s, status=%s WHERE id=%s",
            (username, email, status, id)
        )
        mysql.connection.commit()
        cur.close()

        return redirect(url_for('auth.users_list'))

    # GET request
    cur.execute("SELECT * FROM auth_users WHERE id=%s", (id,))
    user = cur.fetchone()
    cur.close()

    return render_template('edit_user.html', user=user)