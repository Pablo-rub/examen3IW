from flask import Flask, redirect, url_for, request, jsonify, session
from flask_oauthlib.client import OAuth
import requests
from pymongo import MongoClient
from datetime import datetime, timedelta
import os

secretKey = os.getEnv("REACT_APP_SECRET_KEY")
consumerKey = os.getEnv("REACT_APP_CONSUMER_KEY")
consumerSecret = os.getEnv("REACT_APP_CONSUMER_SECRET")
mongoUri = os.getEnv("MONGO_URI")

app = Flask(__name__)
app.secret_key = secretKey
app.config['SESSION_COOKIE_NAME'] = 'your_session_cookie_name'

oauth = OAuth(app)

# Configura el cliente de Google
google = oauth.remote_app(
    'google',
    consumer_key=consumerKey,
    consumer_secret=consumerSecret,
    request_token_params={
        'scope': 'email profile',
    },
    base_url='https://www.googleapis.com/oauth2/v1/',
    request_token_url=None,
    access_token_method='POST',
    access_token_url='https://accounts.google.com/o/oauth2/token',
    authorize_url='https://accounts.google.com/o/oauth2/auth',
)

# Conexión a MongoDB
MONGO_URI = mongoUri
client = MongoClient(MONGO_URI)
db = client["examen3IW"]
login_logs_collection = db["login_logs"]

@app.route('/')
def index():
    return 'Bienvenido a Eventual!'

@app.route('/login')
def login():
    return google.authorize(callback=url_for('authorized', _external=True))

@app.route('/logout')
def logout():
    session.pop('google_token', None)
    session.pop('user_info', None)
    return redirect(url_for('index'))

@app.route('/login/authorized', methods=['GET', 'POST'])
def authorized():
    if request.method == 'POST':
        # Recibe el token de Google desde el frontend
        token = request.json.get('token')
        if not token:
            return jsonify({"success": False, "message": "Token de Google no proporcionado."}), 400

        # Verifica el token con Google
        try:
            response = requests.get(
                'https://www.googleapis.com/oauth2/v3/userinfo',
                headers={'Authorization': f'Bearer {token}'}
            )
            user_info = response.json()

            if response.status_code != 200 or 'error' in user_info:
                return jsonify({"success": False, "message": "Token inválido."}), 400

            # Guarda los detalles del usuario en la sesión
            session['user_info'] = user_info

            # Obtener la expiración del token (ejemplo: 1 hora)
            expires_in = timedelta(seconds=3600)
            expiration_time = datetime.utcnow() + expires_in

            # Registrar en el log
            login_log = {
                "timestamp": datetime.utcnow(),
                "user_email": user_info.get('email'),
                "expiration": expiration_time,
                "token": token
            }
            login_logs_collection.insert_one(login_log)

            return jsonify({"success": True, "message": "Autenticación exitosa"})
        except Exception as e:
            return jsonify({"success": False, "message": str(e)}), 500

@app.route('/profile')
def profile():
    if 'user_info' not in session:
        return redirect(url_for('login'))

    user_info = session.get('user_info', {})
    return f"Tu perfil: {user_info.get('name')}, {user_info.get('email')}"

@google.tokengetter
def get_google_oauth_token():
    return session.get('google_token')

if __name__ == '__main__':
    app.run(debug=True)
