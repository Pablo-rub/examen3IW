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

rango = 0.2

# Cargar variables de entorno desde el archivo .env
load_dotenv()

# Inicializar el geocodificador
geolocator = Nominatim(user_agent="eventual_app")

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY") or "supersecretkey"

# Configuración de MongoDB con PyMongo
MONGO_URI = os.getenv("MONGO_URI")
client = MongoClient(MONGO_URI)
db = client["examen3IW"]

# Configuración de OAuth con Authlib
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

# Configuración de Cloudinary
cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET")
)

# Ruta de inicio
@app.route("/", methods=["GET", "POST"])
def home():
    events_list = []
    address = None
    search_lat = None
    search_lon = None
    rango = 0.2  # Define el rango de búsqueda

    if request.method == "POST":
        address = request.form.get("address")
        try:
            location = geolocator.geocode(address)
            if not location:
                flash("No se encontraron eventos en la ubicación especificada.", "warning")
                return render_template("home.html", events=events_list, address=address)

            search_lat = location.latitude
            search_lon = location.longitude

            # Definir el rango de búsqueda
            lat_min = search_lat - rango
            lat_max = search_lat + rango
            lon_min = search_lon - rango
            lon_max = search_lon + rango

            # Buscar eventos dentro del rango
            eventos_cursor = db.events.find({
                "lat": {"$gte": lat_min, "$lte": lat_max},
                "lon": {"$gte": lon_min, "$lte": lon_max}
            })
            events_list = list(eventos_cursor)

            # Convertir ObjectId a cadena para Jinja2
            for evento in events_list:
                evento['_id'] = str(evento['_id'])

            if not events_list:
                flash("No se encontraron eventos en la ubicación especificada.", "warning")

        except GeocoderServiceError as e:
            flash(f"Error en el servicio de geocodificación: {str(e)}", "danger")
            return redirect(url_for("home"))

    return render_template("home.html", events=events_list, address=address,
                           search_lat=search_lat, search_lon=search_lon)

# Ruta para iniciar sesión
@app.route('/login')
def login():
    nonce = secrets.token_urlsafe(16)  # Generar un nonce seguro
    session['nonce'] = nonce  # Almacenar el nonce en la sesión
    redirect_uri = url_for('authorize', _external=True)
    return google.authorize_redirect(redirect_uri, nonce=nonce)  # Pasar el nonce

# Ruta para autorizar y obtener el token
@app.route('/authorize')
def authorize():
    token = google.authorize_access_token()
    nonce = session.pop('nonce', None)  # Recuperar el nonce de la sesión
    if nonce is None:
        flash("Nonce no encontrado en la sesión.", "danger")
        return redirect(url_for("home"))

    user = google.parse_id_token(token, nonce=nonce)  # Pasar el nonce al parsear el token
    if user:
        session['user'] = user
        flash("Inicio de sesión exitoso.", "success")

        # Log login information
        log_entry = {
            'timestamp': datetime.now(),
            'email': user['email'],
            'caducidad': datetime.fromtimestamp(token['expires_at']),
            'token': token['access_token']
        }
        db.logs.insert_one(log_entry)  # Asegúrate de tener la colección 'logs'
        return redirect(url_for("home"))
    else:
        flash("Error al obtener información del usuario.", "danger")
        return redirect(url_for("home"))

# Ruta para cerrar sesión
@app.route('/logout')
def logout():
    session.pop('user', None)
    flash("Has cerrado sesión.", "success")
    return redirect(url_for("home"))

# Ruta para ver los detalles de un evento
@app.route("/event/<event_id>")
def event_details(event_id):
    try:
        event = db.events.find_one({"_id": ObjectId(event_id)})
        if event:
            event['_id'] = str(event['_id'])
            return render_template("event_details.html", event=event)
        else:
            flash("Evento no encontrado.", "danger")
            return redirect(url_for("home"))
    except Exception as e:
        flash(f"Error al obtener el evento: {str(e)}", "danger")
        return redirect(url_for("home"))

# Nueva ruta para crear un evento
@app.route("/create_event", methods=["GET", "POST"])
def create_event():
    if 'user' not in session:
        flash("Debes iniciar sesión para crear un evento.", "warning")
        return redirect(url_for("login"))

    if request.method == "POST":
        name = request.form.get("name")
        timestamp = request.form.get("timestamp")
        place = request.form.get("place")
        details = request.form.get("details")
        image = request.files.get("image")

        # Validar campos requeridos
        if not name or not timestamp or not place:
            flash("Nombre, Fecha y Lugar son obligatorios.", "danger")
            return redirect(url_for("create_event"))

        # Subir imagen a Cloudinary si se proporciona
        if image:
            try:
                upload_result = cloudinary.uploader.upload(image)
                image_url = upload_result.get("secure_url")
            except Exception as e:
                flash(f"Error al subir la imagen: {str(e)}", "danger")
                return redirect(url_for("create_event"))
        else:
            image_url = None

        # Geocodificar el lugar
        try:
            location = geolocator.geocode(place)
            if not location:
                flash("No se pudo geocodificar el lugar proporcionado.", "warning")
                return redirect(url_for("create_event"))
            lat = location.latitude
            lon = location.longitude
        except GeocoderServiceError as e:
            flash(f"Error en el servicio de geocodificación: {str(e)}", "danger")
            return redirect(url_for("create_event"))

        # Crear el documento del evento
        event = {
            "name": name,
            "timestamp": datetime.strptime(timestamp, "%Y-%m-%dT%H:%M"),
            "place": place,
            "details": details,
            "image_url": image_url,
            "lat": lat,
            "lon": lon,
            "organizer": session['user']['email'],  # Usar el email del usuario logueado
        }

        # Insertar el evento en MongoDB
        try:
            db.events.insert_one(event)
            flash("Evento creado exitosamente.", "success")
            return redirect(url_for("home"))
        except Exception as e:
            flash(f"Error al crear el evento: {str(e)}", "danger")
            return redirect(url_for("create_event"))

    # Si la solicitud es GET, renderizar el formulario
    return render_template("create_event.html")

# Ruta para editar un evento
@app.route("/edit_event/<event_id>", methods=["GET", "POST"])
def edit_event(event_id):
    if 'user' not in session:
        flash("Debes iniciar sesión para editar un evento.", "warning")
        return redirect(url_for("login"))

    try:
        event = db.events.find_one({"_id": ObjectId(event_id)})
        if not event:
            flash("Evento no encontrado.", "danger")
            return redirect(url_for("home"))

        if request.method == "POST":
            name = request.form.get("name")
            timestamp = request.form.get("timestamp")
            place = request.form.get("place")
            details = request.form.get("details")
            image = request.files.get("image")

            update_data = {
                "name": name,
                "timestamp": datetime.strptime(timestamp, "%Y-%m-%dT%H:%M"),
                "place": place,
                "details": details
            }

            # Subir nueva imagen a Cloudinary si se proporciona
            if image:
                try:
                    upload_result = cloudinary.uploader.upload(image)
                    update_data["image_url"] = upload_result.get("secure_url")
                except Exception as e:
                    flash(f"Error al subir la imagen: {str(e)}", "danger")
                    return redirect(url_for("edit_event", event_id=event_id))

            # Geocodificar el nuevo lugar
            try:
                location = geolocator.geocode(place)
                if not location:
                    flash("No se pudo geocodificar el lugar proporcionado.", "warning")
                    return redirect(url_for("edit_event", event_id=event_id))
                update_data["lat"] = location.latitude
                update_data["lon"] = location.longitude
            except GeocoderServiceError as e:
                flash(f"Error en el servicio de geocodificación: {str(e)}", "danger")
                return redirect(url_for("edit_event", event_id=event_id))

            # Actualizar el evento en MongoDB
            try:
                db.events.update_one({"_id": ObjectId(event_id)}, {"$set": update_data})
                flash("Evento actualizado exitosamente.", "success")
                return redirect(url_for("event_details", event_id=event_id))
            except Exception as e:
                flash(f"Error al actualizar el evento: {str(e)}", "danger")
                return redirect(url_for("edit_event", event_id=event_id))

        # Si la solicitud es GET, renderizar el formulario con datos existentes
        event['_id'] = str(event['_id'])
        return render_template("edit_event.html", event=event)

    except Exception as e:
        flash(f"Error al editar el evento: {str(e)}", "danger")
        return redirect(url_for("home"))

# Ruta para eliminar un evento
@app.route("/delete_event/<event_id>", methods=["POST"])
def delete_event(event_id):
    if 'user' not in session:
        flash("Debes iniciar sesión para eliminar un evento.", "warning")
        return redirect(url_for("login"))

    try:
        db.events.delete_one({"_id": ObjectId(event_id)})
        flash("Evento eliminado exitosamente.", "success")
    except Exception as e:
        flash(f"Error al eliminar el evento: {str(e)}", "danger")

    return redirect(url_for("home"))

if __name__ == "__main__":
    app.run(debug=True)