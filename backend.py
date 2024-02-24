from googlemaps import Client

# Replace with your API key
api_key = "YOUR_API_KEY"

# Create a client object
gmaps = Client(key=api_key)

# Geocode an address
address = "1600 Pennsylvania Avenue NW, Washington, DC"
geocode_result = gmaps.geocode(address)

# Print the latitude and longitude
print(f"Latitude: {geocode_result[0]['geometry']['location']['lat']}")
print(f"Longitude: {geocode_result[0]['geometry']['location']['lng']}")
