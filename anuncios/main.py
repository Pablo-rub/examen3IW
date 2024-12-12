from flask import Flask, render_template, redirect, url_for, request, flash
from flask_pymongo import PyMongo
from flask_dance.contrib.google import make_google_blueprint, google
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user, login_required
from functools import wraps
from datetime import datetime, timedelta
from geopy.geocoders import Nominatim
import cloudinary
import cloudinary.uploader
import os
from dotenv import load_dotenv
from bson import ObjectId
from math import radians, cos, sin, sqrt, atan2

# Cargar variables de entorno
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY") or "supersecretkey"

# Configuración de MongoDB
app.config["MONGO_URI"] = os.getenv("MONGO_URI")
mongo = PyMongo(app)
db = mongo.db

# Verificación de la conexión
if db:
    print("Conexión a MongoDB establecida correctamente.")
else:
    print("Error al conectar con MongoDB.")

# Configuración de Cloudinary
cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET"),
)

# Configuración de OAuth2 con Google
google_bp = make_google_blueprint(
    client_id=os.getenv("GOOGLE_CLIENT_ID"),
    client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
    scope=["profile", "email"],
    redirect_url="/login/authorized",
)
app.register_blueprint(google_bp, url_prefix="/login")

# Configuración de Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

# Obtener correos de administradores desde variables de entorno
admin_emails = os.getenv("ADMIN_EMAILS", "").split(",")

@app.context_processor
def inject_admin_emails():
    return dict(admin_emails=admin_emails)

# Usuario de ejemplo para Flask-Login
class User(UserMixin):
    def __init__(self, id, email):
        self.id = id
        self.email = email

# Función para cargar el usuario
@login_manager.user_loader
def load_user(user_id):
    user = db.users.find_one({"_id": ObjectId(user_id)})
    if user:
        return User(str(user["_id"]), user["email"])
    return None

# Decorador para rutas que requieren ser el organizador del evento
def organizer_required(f):
    @wraps(f)
    def decorated_function(event_id, *args, **kwargs):
        event = db.events.find_one({"_id": ObjectId(event_id)})
        if not event:
            flash("Evento no encontrado.", "danger")
            return redirect(url_for('home'))
        if event["organizer"] != current_user.email:
            flash("No tienes permiso para modificar este evento.", "danger")
            return redirect(url_for('home'))
        return f(event_id, *args, **kwargs)
    return decorated_function

# Decorador para rutas que requieren ser administrador
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.email not in admin_emails:
            flash("No tienes permiso para acceder a los logs.", "danger")
            return redirect(url_for('home'))
        return f(*args, **kwargs)
    return decorated_function

# Ruta de inicio
@app.route("/")
def home():
    return render_template("home.html")

# Ruta de inicio de sesión
@app.route("/login")
def login():
    if not current_user.is_authenticated:
        return redirect(url_for("google.login"))
    return redirect(url_for("home"))

# Ruta autorizada después de login
@app.route("/login/authorized")
def authorized():
    if not google.authorized:
        flash("Autenticación fallida.", "danger")
        return redirect(url_for("home"))
    resp = google.get("/oauth2/v2/userinfo")
    if not resp.ok:
        flash("No se pudo obtener información del usuario.", "danger")
        return redirect(url_for("home"))
    user_info = resp.json()
    user = db.users.find_one({"email": user_info["email"]})
    if not user:
        # Crear nuevo usuario en la base de datos
        user_id = db.users.insert_one({"email": user_info["email"]}).inserted_id
        user = db.users.find_one({"_id": user_id})
    login_user(User(str(user["_id"]), user["email"]))

    # Registrar el login en los logs
    token = google.token["access_token"]
    expiration = datetime.utcnow() + timedelta(hours=1)  # Asumiendo token válido por 1 hora
    db.login_logs.insert_one({
        "timestamp": datetime.utcnow(),
        "user_email": user_info["email"],
        "expiration": expiration,
        "token": token
    })

    flash("Inicio de sesión exitoso.", "success")
    return redirect(url_for("home"))

# Ruta de cierre de sesión
@app.route("/logout")
@login_required
def logout():
    # Registrar el logout en los logs
    token = google.token.get("access_token", "unknown")
    db.login_logs.insert_one({
        "timestamp": datetime.utcnow(),
        "user_email": current_user.email,
        "expiration": datetime.utcnow(),
        "token": token
    })

    logout_user()
    flash("Cierre de sesión exitoso.", "success")
    return redirect(url_for("home"))

# Ruta para crear un nuevo evento
@app.route("/create-event", methods=["GET", "POST"])
@login_required
def create_event():
    if request.method == "POST":
        name = request.form.get("name")
        timestamp = request.form.get("timestamp")
        place = request.form.get("place")
        image = request.files.get("image")

        if not all([name, timestamp, place]):
            flash("Todos los campos son requeridos.", "danger")
            return redirect(url_for("create_event"))

        # Geocodificar la dirección
        coords = obtener_coordenadas(place)
        if not coords:
            flash("No se pudieron obtener coordenadas para la dirección proporcionada.", "danger")
            return redirect(url_for("create_event"))

        # Cargar imagen a Cloudinary
        if image:
            upload_result = cloudinary.uploader.upload(image)
            image_url = upload_result.get("secure_url")
        else:
            image_url = None

        event = {
            "name": name,
            "timestamp": datetime.strptime(timestamp, "%Y-%m-%dT%H:%M"),
            "place": place,
            "lat": coords["lat"],
            "lon": coords["lon"],
            "organizer": current_user.email,
            "image": image_url
        }

        db.events.insert_one(event)
        flash("Evento creado exitosamente.", "success")
        return redirect(url_for("home"))

    return render_template("create_event.html")

# Ruta para ver detalles de un evento
@app.route("/event/<event_id>")
def event_details(event_id):
    event = db.events.find_one({"_id": ObjectId(event_id)})
    if not event:
        flash("Evento no encontrado.", "danger")
        return redirect(url_for("home"))
    event["_id"] = str(event["_id"])
    return render_template("event_details.html", event=event)

# Ruta para editar un evento
@app.route("/edit-event/<event_id>", methods=["GET", "POST"])
@login_required
@organizer_required
def edit_event(event_id):
    event = db.events.find_one({"_id": ObjectId(event_id)})
    if not event:
        flash("Evento no encontrado.", "danger")
        return redirect(url_for("home"))
    event["_id"] = str(event["_id"])

    if request.method == "POST":
        name = request.form.get("name")
        timestamp = request.form.get("timestamp")
        place = request.form.get("place")
        image = request.files.get("image")

        update_data = {}
        if name:
            update_data["name"] = name
        if timestamp:
            update_data["timestamp"] = datetime.strptime(timestamp, "%Y-%m-%dT%H:%M")
        if place:
            coords = obtener_coordenadas(place)
            if not coords:
                flash("No se pudieron obtener coordenadas para la dirección proporcionada.", "danger")
                return redirect(url_for("edit_event", event_id=event_id))
            update_data["place"] = place
            update_data["lat"] = coords["lat"]
            update_data["lon"] = coords["lon"]
        if image:
            upload_result = cloudinary.uploader.upload(image)
            update_data["image"] = upload_result.get("secure_url")

        if update_data:
            db.events.update_one({"_id": ObjectId(event_id)}, {"$set": update_data})
            flash("Evento actualizado exitosamente.", "success")
            return redirect(url_for("event_details", event_id=event_id))
        else:
            flash("No hay datos para actualizar.", "warning")
            return redirect(url_for("edit_event", event_id=event_id))

    return render_template("edit_event.html", event=event)

# Ruta para eliminar un evento
@app.route("/delete-event/<event_id>", methods=["POST"])
@login_required
@organizer_required
def delete_event(event_id):
    db.events.delete_one({"_id": ObjectId(event_id)})
    flash("Evento eliminado exitosamente.", "success")
    return redirect(url_for("home"))

# Ruta para ver los logs (solo administradores)
@app.route("/logs")
@login_required
@admin_required
def logs():
    logs_cursor = db.login_logs.find().sort("timestamp", -1).limit(100)
    logs = []
    for log in logs_cursor:
        logs.append({
            "timestamp": log["timestamp"],
            "user_email": log["user_email"],
            "expiration": log["expiration"],
            "token": log["token"]
        })
    return render_template("logs.html", logs=logs)

# Ruta para buscar eventos cercanos
@app.route("/search", methods=["GET"])
def search_events():
    address = request.args.get("address")
    if not address:
        flash("Dirección requerida.", "danger")
        return redirect(url_for("home"))

    # Geocodificar la dirección
    coords = obtener_coordenadas(address)
    if not coords:
        flash("No se pudo geocodificar la dirección proporcionada.", "danger")
        return redirect(url_for("home"))

    lat = coords["lat"]
    lon = coords["lon"]

    # Calcular eventos dentro de 0.2 unidades
    events_cursor = db.events.find()
    nearby_events = []
    for event in events_cursor:
        distance = calculate_distance(lat, lon, event["lat"], event["lon"])
        if distance <= 0.2:
            event["_id"] = str(event["_id"])
            nearby_events.append(event)

    # Ordenar por timestamp descendente
    nearby_events = sorted(nearby_events, key=lambda x: x["timestamp"], reverse=True)

    return render_template("home.html", events=nearby_events, location={"lat": lat, "lon": lon}, address=address)

# Función para calcular distancia usando la fórmula de Haversine
def calculate_distance(lat1, lon1, lat2, lon2):
    # Convertir de grados a radianes
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    # Fórmula de Haversine
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    # Radio de la Tierra en kilómetros
    r = 6371
    return r * c

# Función para geocodificar una dirección
def obtener_coordenadas(direccion):
    geolocator = Nominatim(user_agent="eventual_app")
    ubicacion = geolocator.geocode(direccion)
    if ubicacion:
        return {
            'lat': ubicacion.latitude,
            'lon': ubicacion.longitude
        }
    return None

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
