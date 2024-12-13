import os
from flask import Flask, render_template, request, redirect, url_for, flash, session
from pymongo import MongoClient
from dotenv import load_dotenv
from bson.objectid import ObjectId
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderServiceError
from authlib.integrations.flask_client import OAuth
import cloudinary
import cloudinary.uploader
from datetime import datetime
import secrets  # Importar para generar nonce
from bson import json_util  # Importar json_util

# Cargar variables de entorno
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY") or "supersecretkey"

# Configuración de MongoDB
MONGO_URI = os.getenv("MONGO_URI")
client = MongoClient(MONGO_URI)
db = client["mimapa_db"]  # Base de datos específica

# Configuración de Cloudinary
cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET")
)

# Configuración de OAuth
oauth = OAuth(app)
google = oauth.register(
    name='google',
    client_id=os.getenv('GOOGLE_CLIENT_ID'),
    client_secret=os.getenv('GOOGLE_CLIENT_SECRET'),
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={
        'scope': 'openid profile email'
    }
)

geolocator = Nominatim(user_agent="mimapa_app")

# Ruta de inicio
@app.route('/')
def index():
    if 'user' in session:
        return redirect(url_for('my_map'))
    return render_template('index.html')

# Ruta para iniciar sesión
@app.route('/login')
def login():
    nonce = secrets.token_urlsafe(16)
    session['nonce'] = nonce
    redirect_uri = url_for('authorize', _external=True)
    return google.authorize_redirect(redirect_uri, nonce=nonce)

@app.route('/authorize')
def authorize():
    token = google.authorize_access_token()
    nonce = session.pop('nonce', None)
    user_info = google.parse_id_token(token, nonce=nonce)

    if user_info:
        session['user'] = {
            'email': user_info['email'],
            'token': token['access_token']
        }
        flash('Inicio de sesión exitoso.', 'success')
        return redirect(url_for('my_map'))
    else:
        flash('Error al iniciar sesión.', 'danger')
        return redirect(url_for('index'))

# Ruta para cerrar sesión
@app.route('/logout')
def logout():
    session.pop('user', None)
    flash('Has cerrado sesión.', 'success')
    return redirect(url_for('index'))

# Ruta para mostrar el mapa del usuario actual
@app.route('/my_map', methods=['GET', 'POST'])
def my_map():
    if 'user' not in session:
        flash('Debes iniciar sesión para ver tu mapa.', 'warning')
        return redirect(url_for('login'))

    user_email = session['user']['email']

    if request.method == 'POST':
        location_name = request.form.get('location')
        image = request.files.get('image')

        # Geocoding
        try:
            location = geolocator.geocode(location_name)
            if not location:
                flash('No se pudo encontrar la ubicación.', 'warning')
                return redirect(url_for('my_map'))

            lat = location.latitude
            lon = location.longitude

            # Subir imagen a Cloudinary
            image_url = None
            if image:
                upload_result = cloudinary.uploader.upload(image)
                image_url = upload_result.get('secure_url')

            # Guardar marcador en la base de datos
            marker = {
                'email': user_email,
                'location_name': location_name,
                'lat': lat,
                'lon': lon,
                'image_url': image_url
            }
            db.markers.insert_one(marker)
            flash('Marcador añadido exitosamente.', 'success')

        except Exception as e:
            flash(f'Error al añadir el marcador: {e}', 'danger')

    # Recuperar marcadores del usuario y convertir ObjectId a str
    markers_cursor = db.markers.find({'email': user_email})
    markers = []
    for marker in markers_cursor:
        marker['_id'] = str(marker['_id'])
        markers.append(marker)

    # Recuperar imágenes del usuario
    images = [marker['image_url'] for marker in markers if marker.get('image_url')]

    return render_template('my_map.html', markers=markers, images=images, user_email=user_email)

# Ruta para ver el mapa de otro usuario
@app.route('/map', methods=['GET', 'POST'])
def view_map():
    if 'user' not in session:
        flash('Debes iniciar sesión para ver mapas.', 'warning')
        return redirect(url_for('login'))

    if request.method == 'POST':
        other_user_email = request.form.get('email')

        # Recuperar marcadores del otro usuario y convertir ObjectId a str
        markers_cursor = db.markers.find({'email': other_user_email})
        markers = []
        for marker in markers_cursor:
            marker['_id'] = str(marker['_id'])
            markers.append(marker)

        if not markers:
            flash('No se encontraron marcadores para este usuario.', 'warning')
            return redirect(url_for('view_map'))

        # Registrar la visita
        visit = {
            'visited_email': other_user_email,
            'visitor_email': session['user']['email'],
            'timestamp': datetime.now(),
            'token': session['user']['token']
        }
        db.visits.insert_one(visit)

        # Recuperar visitas y convertir ObjectId a str
        visits_cursor = db.visits.find({'visited_email': other_user_email}).sort('timestamp', -1)
        visits = []
        for visit in visits_cursor:
            visit['_id'] = str(visit['_id'])
            visits.append(visit)

        # Recuperar imágenes
        images = [marker['image_url'] for marker in markers if marker.get('image_url')]

        return render_template('view_map.html', markers=markers, images=images, visits=visits, user_email=other_user_email)

    return render_template('view_map_form.html')

if __name__ == '__main__':
    app.run(debug=True)