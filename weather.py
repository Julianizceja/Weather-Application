import requests
from PIL import Image, ImageTk  # Import Image and ImageTk from Pillow
import geocoder
import tkinter as tk
import io  # For handling byte streams
from datetime import datetime

API_KEY = 'd22608d632cd6a389dc448f6d67a26c4'
BASE_URL = 'https://api.openweathermap.org/data/2.5/weather'

# Paths to your custom .png images
IMAGE_A_PATH = 'https://assets.caseys.com/m/032adf8b98e5fe3d/400x400-5200013513_base.PNG'  # For 80°F or more
IMAGE_B_PATH = 'https://assets.caseys.com/m/ba4364deb154dd59/400x400-5200032481_base.PNG'  # For 70°F or less
IMAGE_C_PATH = 'https://assets.caseys.com/m/4899e0cfa23bacbf/400x400-5200010241_base.PNG'  # For rainy weather

dark_mode_colors = {
    "bg": "#121212",        # Background color
    "fg": "#ffffff",        # Text color
    "button_bg": "#1f1f1f", # Button background
    "button_fg": "#ffffff"  # Button text color
}

light_mode_colors = {
    "bg": "#ffffff",
    "fg": "#000000",
    "button_bg": "#f0f0f0",
    "button_fg": "#000000"
}

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
            daily_forecast.append(f"{forecast_date}: {temp}°F, {weather_description}")
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


def apply_theme(popup, theme_colors):
    # Update the popup's background
    popup.config(bg=theme_colors["bg"])

    # Update all child widgets
    for widget in popup.winfo_children():
        if isinstance(widget, tk.Label):
            widget.config(bg=theme_colors["bg"], fg=theme_colors["fg"])
        elif isinstance(widget, tk.Button):
            widget.config(bg=theme_colors["button_bg"], fg=theme_colors["button_fg"])

def toggle_mode(popup, is_dark_mode_container):
    is_dark_mode = is_dark_mode_container[0]  # Get the current state
    if is_dark_mode:
        apply_theme(popup, light_mode_colors)  # Switch to light mode
    else:
        apply_theme(popup, dark_mode_colors)  # Switch to dark mode
    is_dark_mode_container[0] = not is_dark_mode  # Toggle the state




def show_popup(weather_data, forecast_data):
    
    global current_theme
    current_theme = light_mode_colors  # Default theme is light
    
    # Mutable container to track dark mode status
    is_dark_mode_container = [False]
    
    
    # Create a new tkinter window
    root = tk.Tk()
    # root.withdraw()  # Hide the main window

    # Create a new window for the popup
    popup = tk.Toplevel()
    popup.overrideredirect(True)  # Remove window borders and title bar
    popup.wm_attributes("-topmost", True)  # Keep the window on top
    popup.geometry("+100+100")  # Set the popup's position
    apply_theme(popup, current_theme)  # Apply the initial theme


    # Set transparency (Windows: make a specific color transparent)
    # popup.wm_attributes("-alpha", 0)

    # Set transparency (macOS: make the entire window transparent)
    # popup.wm_attributes("-transparent", True)

    # Create a message to show in the popup
    message = (f"City: {weather_data['name']}\n"
               f"Temperature: {weather_data['main']['temp']}°F\n"
               f"Weather: {weather_data['weather'][0]['description']}")

    # Get the image based on weather conditions
    weather_image = get_image_based_on_weather(weather_data)

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



     # Toggle Button
    toggle_button = tk.Button(
        popup,
        text="Toggle Dark Mode",
        command=lambda: toggle_mode(popup, is_dark_mode_container)
    )
    toggle_button.pack(pady=10)

    # Add a close button (Optional)
    close_button = tk.Button(popup, text="Close", command=lambda: [popup.destroy(), root.quit()])
    close_button.pack(pady=10)

    # Run the popup loop
    root.mainloop()

# Get the user's location based on their IP address
g = geocoder.ip('me')
lat, lon = g.latlng

weather_data = get_weather(lat, lon)
forecast_data = get_weather_forecast(lat, lon)

if weather_data and forecast_data:
    show_popup(weather_data, forecast_data)
else:
    # Show an error popup if weather data is not found
    show_popup({"name": "Error", "main": {"temp": ""}, "weather": [{"description": "Weather data not found!"}]})
