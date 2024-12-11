from geopy.geocoders import Nominatim

def obtener_coordenadas(direccion):
    geolocator = Nominatim(user_agent="eventual_app")
    ubicacion = geolocator.geocode(direccion)
    if ubicacion:
        return {
            'lat': ubicacion.latitude,
            'lon': ubicacion.longitude
        }
    return None
