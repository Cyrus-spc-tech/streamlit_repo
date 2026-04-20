from geopy.geocoders import Nominatim

def get_lat_long(location):
    geolocator = Nominatim(user_agent="geopy_example", timeout=10)
    location = geolocator.geocode(location)

    if location:
        latitude, longitude = location.latitude, location.longitude
        return latitude, longitude
    else:
        return None