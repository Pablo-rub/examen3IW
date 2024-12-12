import os
from flask import Flask, render_template, request, redirect, url_for, flash
from pymongo import MongoClient
from dotenv import load_dotenv
from bson.objectid import ObjectId
import cloudinary
import cloudinary.uploader
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderServiceError

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

# Configuración de Cloudinary
cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET")
)

# Ruta de inicio
@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        address = request.form.get("address")
        try:
            location = geolocator.geocode(address)
            if not location:
                flash("No se pudo geocodificar la dirección proporcionada.", "danger")
                return redirect(url_for("home"))
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
            eventos = list(eventos_cursor)  # Convertir Cursor a Lista

            # Convertir ObjectId a String para evitar problemas en Jinja2
            for evento in eventos:
                evento['_id'] = str(evento['_id'])

            if not eventos:
                flash("No se encontraron eventos en la ubicación especificada.", "warning")

            return render_template("home.html", address=address, events=eventos, search_lat=search_lat, search_lon=search_lon)
        except GeocoderServiceError as e:
            flash(f"Error en el servicio de geocodificación: {str(e)}", "danger")
            return redirect(url_for("home"))

    return render_template("home.html")

# Ruta para ver los detalles de un evento
@app.route("/event/<event_id>")
def event_details(event_id):
    try:
        # Buscar el evento por su ID
        event = db.events.find_one({"_id": ObjectId(event_id)})
        if not event:
            flash("Evento no encontrado.", "danger")
            return redirect(url_for("home"))
        
        # Convertir ObjectId a String
        event['_id'] = str(event['_id'])

        return render_template("event_details.html", event=event)
    except Exception as e:
        flash(f"Error al buscar el evento: {str(e)}", "danger")
        return redirect(url_for("home"))

# Nueva ruta para crear un evento
@app.route("/create_event", methods=["GET", "POST"])
def create_event():
    if request.method == "POST":
        name = request.form.get("name")
        timestamp = request.form.get("timestamp")
        place = request.form.get("place")
        image = request.files.get("image")
        details = request.form.get("details", "")
        
        # Validar campos obligatorios
        if not name or not timestamp or not place:
            flash("Por favor, completa todos los campos obligatorios.", "danger")
            return redirect(url_for("create_event"))
        
        # Geocodificar la ubicación
        try:
            location = geolocator.geocode(place)
            if not location:
                flash("No se pudo geocodificar la ubicación proporcionada.", "danger")
                return redirect(url_for("create_event"))
            lat = location.latitude
            lon = location.longitude
        except GeocoderServiceError as e:
            flash(f"Error en el servicio de geocodificación: {str(e)}", "danger")
            return redirect(url_for("create_event"))
        
        # Manejar la carga de la imagen si se proporciona
        image_url = ""

        if image and image.filename != "":
            try:
                upload_result = cloudinary.uploader.upload(image)
                image_url = upload_result.get("secure_url", "")
            except Exception as upload_error:
                flash(f"Error al cargar la imagen: {str(upload_error)}", "danger")
                return redirect(url_for("create_event"))
        
        # Crear el documento del evento
        event_document = {
            "name": name,
            "timestamp": timestamp,
            "place": place,
            "details": details,
            "image_url": image_url,
            "organizer": "Anónimo",  # Dado que no hay autenticación, asignamos "Anónimo"
            "lat": lat,
            "lon": lon
        }
        
        try:
            db.events.insert_one(event_document)
            flash("Evento creado exitosamente.", "success")
            return redirect(url_for("home"))
        except Exception as db_error:
            flash(f"Error al crear el evento: {str(db_error)}", "danger")
            return redirect(url_for("create_event"))
    
    return render_template("create_event.html")

# Ruta para editar un evento
@app.route("/edit_event/<event_id>", methods=["GET", "POST"])
def edit_event(event_id):
    try:
        event = db.events.find_one({"_id": ObjectId(event_id)})
        if not event:
            flash("Evento no encontrado.", "danger")
            return redirect(url_for("home"))
        
        if request.method == "POST":
            name = request.form.get("name")
            timestamp = request.form.get("timestamp")
            place = request.form.get("place")
            image = request.files.get("image")
            details = request.form.get("details", "")
            
            # Validar campos obligatorios
            if not name or not timestamp or not place:
                flash("Por favor, completa todos los campos obligatorios.", "danger")
                return redirect(url_for("edit_event", event_id=event_id))
            
            # Geocodificar la nueva ubicación
            try:
                location = geolocator.geocode(place)
                if not location:
                    flash("No se pudo geocodificar la ubicación proporcionada.", "danger")
                    return redirect(url_for("edit_event", event_id=event_id))
                lat = location.latitude
                lon = location.longitude
            except GeocoderServiceError as e:
                flash(f"Error en el servicio de geocodificación: {str(e)}", "danger")
                return redirect(url_for("edit_event", event_id=event_id))
            
            # Manejar la carga de la imagen si se proporciona
            image_url = event.get("image_url", "")
            if image and image.filename != "":
                try:
                    upload_result = cloudinary.uploader.upload(image)
                    image_url = upload_result.get("secure_url", "")
                except Exception as upload_error:
                    flash(f"Error al cargar la imagen: {str(upload_error)}", "danger")
                    return redirect(url_for("edit_event", event_id=event_id))
            
            # Actualizar el documento del evento
            updated_event = {
                "name": name,
                "timestamp": timestamp,
                "place": place,
                "details": details,
                "image_url": image_url,
                "lat": lat,
                "lon": lon
            }
            
            try:
                db.events.update_one({"_id": ObjectId(event_id)}, {"$set": updated_event})
                flash("Evento actualizado exitosamente.", "success")
                return redirect(url_for("event_details", event_id=event_id))
            except Exception as db_error:
                flash(f"Error al actualizar el evento: {str(db_error)}", "danger")
                return redirect(url_for("edit_event", event_id=event_id))
        
        # Convertir ObjectId a String
        event['_id'] = str(event['_id'])
        return render_template("edit_event.html", event=event)
    except Exception as e:
        flash(f"Error al procesar la solicitud: {str(e)}", "danger")
        return redirect(url_for("home"))

# Ruta para eliminar un evento
@app.route("/delete_event/<event_id>", methods=["POST"])
def delete_event(event_id):
    try:
        result = db.events.delete_one({"_id": ObjectId(event_id)})
        if result.deleted_count == 1:
            flash("Evento eliminado exitosamente.", "success")
        else:
            flash("Evento no encontrado o ya fue eliminado.", "warning")
    except Exception as e:
        flash(f"Error al eliminar el evento: {str(e)}", "danger")
    return redirect(url_for("home"))

if __name__ == "__main__":
    app.run(debug=True)