from serial import Serial
from pynmeagps import NMEAReader
from pynmeagps import latlon2dms, latlon2dmm
from geopy.geocoders import Nominatim

stream = Serial('com3', 9600, timeout=3)
nmr = NMEAReader(stream)
(raw_data, parsed_data) = nmr.read()
print(parsed_data)
#latitude = parsed_data.lat
#longitude = parsed_data.lon
#print(latitude)
#print(longitude)
#coordinates = [parsed_data.lat,parsed_data.lon]

#geolocator = Nominatim(user_agent="MyApp")
#location = geolocator.reverse(coordinates)
#print(location.address)