import requests
from PIL import Image, ImageTk  # Import Image and ImageTk from Pillow
import geocoder
import tkinter as tk
import io  # For handling byte streams
from tkinter import messagebox
from datetime import datetime
from geopy.geocoders import Nominatim

API_KEY = 'd22608d632cd6a389dc448f6d67a26c4'
BASE_URL = 'https://api.openweathermap.org/data/2.5/weather'

# Paths to your custom .png images
IMAGE_A_PATH = 'https://assets.caseys.com/m/032adf8b98e5fe3d/400x400-5200013513_base.PNG'  # For 80°F or more
IMAGE_B_PATH = 'https://assets.caseys.com/m/ba4364deb154dd59/400x400-5200032481_base.PNG'  # For 70°F or less
IMAGE_C_PATH = 'https://assets.caseys.com/m/4899e0cfa23bacbf/400x400-5200010241_base.PNG'  # For rainy weather

def geocode(location):
    #initialize geocoder
    geolocator = Nominatim(user_agent="weatherproject")#required parameter by OpenStreetMap to track usage
    #geocode location can be just city name or city name and state
    coordinates = geolocator.geocode(location)

    #check to see if geocode found location
    if coordinates:
        return{
            "lat": coordinates.latitude,
            "lon": coordinates.longitude
        }
    else:
        return None

def get_weather(lat, lon):
    params = {
        'lat': lat,
        'lon': lon,
        'appid': API_KEY,
        'units': 'imperial',  # Get temperature in Fahrenheit
    }
    response = requests.get(BASE_URL, params=params)
    if response.status_code == 200:
        return response.json()  # Consistent indentation
    else:
        return None

def get_weather_forecast(lat, lon):
    params = {
        'lat': lat,
        'lon': lon,
        'appid': API_KEY,
        'units': 'imperial'
    }
    response = requests.get('https://api.openweathermap.org/data/2.5/forecast', params=params)
    if response.status_code == 200:
        return response.json()
    else:
        return None

def format_forecast(forecast_data):
    daily_forecast = []
    current_day = None
    for item in forecast_data['list']:
        # Extract the day from the datetime
        forecast_date = datetime.utcfromtimestamp(item['dt']).strftime('%A, %B %d')
        temp = item['main']['temp']
        weather_description = item['weather'][0]['description']

        if current_day != forecast_date:
            daily_forecast.append(f"{forecast_date}: {temp:.1f}°F, {weather_description}")
            current_day = forecast_date

        # Show only one entry per day
        if len(daily_forecast) >= 5:
            break
    return daily_forecast

def download_image(image_url):
    response = requests.get(image_url)
    if response.status_code == 200:
        image_data = io.BytesIO(response.content)
        return Image.open(image_data)  # Use Pillow to open the image
    else:
        return None

def get_image_based_on_weather(weather_data):
    temperature = weather_data['main']['temp']
    weather_description = weather_data['weather'][0]['description'].lower()

    # Determine which image to show based on temperature or rain
    if 'rain' in weather_description:
        image_path = IMAGE_C_PATH  # Rainy weather image
    elif temperature >= 80:
        image_path = IMAGE_A_PATH  # Hot weather image
    elif temperature <= 70:
        image_path = IMAGE_B_PATH  # Cool weather image
    else:
        image_path = IMAGE_A_PATH  # Default image (you can modify this as needed)

    # Download and return the selected image using Pillow
    return download_image(image_path)

def show_popup(weather_data, forecast_data):
    # Create a new tkinter window
    root = tk.Tk()
    root.withdraw()  # Hide the main window

    # Create a new window for the popup
    popup = tk.Toplevel()
    popup.title("Weather App")
    #popup.overrideredirect(True)  # Remove window borders and title bar
    popup.wm_attributes("-topmost", True)  # Keep the window on top
    #popup.geometry("+100+5")  # Set the popup's position
    popup.geometry("900x1000")
    # Set transparency (Windows: make a specific color transparent)
    # popup.wm_attributes("-alpha", 0)

    # Set transparency (macOS: make the entire window transparent)
    # popup.wm_attributes("-transparent", True)

    # Create a message to show in the popup
    message = (f"City: {weather_data['name']}\n"
               f"Temperature: {weather_data['main']['temp']:.1f}°F\n"
               f"Weather: {weather_data['weather'][0]['description']}")

    # Get the image based on weather conditions
    weather_image = get_image_based_on_weather(weather_data)

    #resize image might need to use if we use a different pictures
    #resized_weather_image = weather_image.resize((400,400), Image.LANCZOS)
    
    # Create a Tkinter-compatible photo image
    weather_image_tk = ImageTk.PhotoImage(weather_image)

    # Create a label for the message with a transparent background
    message_label = tk.Label(popup, text=message, padx=10, pady=10, fg="black")
    message_label.pack()

    # Create a label for the image with a transparent background
    image_label = tk.Label(popup, image=weather_image_tk)
    image_label.image = weather_image_tk  # Keep a reference to avoid garbage collection
    image_label.pack()

     # Show the forecast
    forecast_label = tk.Label(popup, text="5-Day Forecast:", padx=10, pady=10, fg="black", font=("Helvetica", 14, "bold"))
    forecast_label.pack()

    # Format and display forecast for 5 days
    forecast_data = format_forecast(forecast_data)
    for day_forecast in forecast_data:
        forecast_day_label = tk.Label(popup, text=day_forecast, padx=10, pady=5, fg="black")
        forecast_day_label.pack()

    # Ensure the popup window updates its layout to accommodate the image
    popup.update_idletasks()  # Forces the window to update its size after adding widgets


    # Add a close button (Optional)
    close_button = tk.Button(popup, text="Close", command=lambda: [popup.destroy(), root.quit()])
    close_button.pack(pady=10)

    # Run the popup loop
    root.mainloop()

def setup_weather_app():
    root = tk.Tk()
    root.title("Weather App")
    root.geometry("500x500")

    global typed_location_entry
    
    tk.Button(root, text="Current Location", font=('Times', 18), command=show_current_location_weather).pack()

    tk.Label(root, text="Type in Location: ", font=('Times', 18)).pack()
    typed_location_entry = tk.Entry(root, width=10, font=('Times', 18))
    typed_location_entry.pack()

    tk.Button(root, text="Get Weather", font=('Times', 18), command=show_typed_location_weather).pack()

    root.mainloop()

def show_current_location_weather(event=None):
    # Get the user's location based on their IP address
    g = geocoder.ip('me')
    lat, lon = g.latlng
    #print(f"lat2 = {lat}, lon = {lon}")

    weather_data = get_weather(lat, lon)
    forecast_data = get_weather_forecast(lat, lon)

    if weather_data and forecast_data:
        show_popup(weather_data, forecast_data)
    else:
        # Show an error popup if weather data is not found
        show_popup({"name": "Error", "main": {"temp": ""}, "weather": [{"description": "Weather data not found!"}]})

def show_typed_location_weather(event=None):
    #get coordinates of typed in location
    coordinates = geocode(typed_location_entry.get().strip())

    if coordinates:
        weather_data = get_weather(coordinates['lat'], coordinates['lon'])
        forecast_data = get_weather_forecast(coordinates['lat'], coordinates['lon'])

        if weather_data and forecast_data:
            show_popup(weather_data, forecast_data)
        else:
            # Show an error popup if weather data is not found
            show_popup({"name": "Error", "main": {"temp": ""}, "weather": [{"description": "Weather data not found!"}]})
        
    else:
        messagebox.showerror("Location Error", "Please type in valid location")

    
    

setup_weather_app()


