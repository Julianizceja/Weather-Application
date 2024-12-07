import requests
from PIL import Image, ImageTk, ImageSequence  # Import Image and ImageTk from Pillow
import geocoder
import tkinter as tk
import io  # For handling byte streams
from tkinter import messagebox
from datetime import datetime
from geopy.geocoders import Nominatim

API_KEY = 'd22608d632cd6a389dc448f6d67a26c4'
BASE_URL = 'https://api.openweathermap.org/data/2.5/weather'
FIVE_DAY_FORECAST_URL = 'https://api.openweathermap.org/data/2.5/forecast'
HOURLY_FORECAST_URL = 'https://pro.openweathermap.org/data/2.5/forecast/hourly'

# Paths to your custom .png images
IMAGE_A_PATH = 'https://i.pinimg.com/originals/67/93/45/679345808c0a740e7aec8ff270192d23.gif'  # Hot weather GIF
IMAGE_B_PATH = 'https://media.tenor.com/EzU33OqujNsAAAAi/glaceon-eevee.gif'  # Cool weather GIF
IMAGE_C_PATH = 'https://www.shinyhunters.com/images/regular/134.gif'  # Rainy weather GIF

LOGO_PATH = 'https://cdn.dribbble.com/users/261567/screenshots/1099769/media/dc312e3c221f0d241ba081535d826eb3.gif'
CLEAR_SKY_PATH = 'https://cdn.pixabay.com/animation/2023/02/02/16/08/16-08-07-79_512.gif' # Clear sky gif
RAIN_PATH = 'https://i.pinimg.com/originals/fa/c4/37/fac4371005100d7465f3b533bac3d9b8.gif' #rain gif
FREEZING_PATH = 'https://media1.tenor.com/m/X-bEkviklBkAAAAC/cold-cold-outside.gif' #freezing weather gif
HOT_PATH = 'https://media.tenor.com/naQ21gHuAhYAAAAM/kitty-hot.gif' #hot weather gif
COLD_PATH = 'https://i.giphy.com/media/v1.Y2lkPTc5MGI3NjExMHA0dGd1YTlzMXcxdDVzODgzZzNncTFrbjI1ejZ4ZDRqaThyNDVpeCZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/xT5JwTOtTZzzldjoZ2/giphy.gif'


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
    response = requests.get(FIVE_DAY_FORECAST_URL, params=params)
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

def animate_gif(label, frames, delay):
    def update(index):
        frame = frames[index]
        label.config(image=frame)
        label.image = frame
        label.after(delay, update, (index + 1) % len(frames))

    update(0)

def get_image_based_on_weather(weather_data, theme="Default"):
    temperature = weather_data['main']['temp']
    weather_description = weather_data['weather'][0]['description']

    # Theme-based image selection
    if theme == "Rainy":
        image_path = IMAGE_C_PATH
    elif theme == "Sunny":
        image_path = IMAGE_A_PATH
    elif theme == "Snowy":
        image_path = IMAGE_SNOWY_PATH
    else:
        # Default behavior
        if 'rain' in weather_description:
            image_path = RAIN_PATH
        elif temperature >= 80:
            image_path = HOT_PATH
        elif temperature <= 70 and temperature > 60:
            image_path = COLD_PATH
        elif temperature <= 60:
            image_path = FREEZING_PATH
        else:
            image_path = IMAGE_A_PATH
    
    # Download and return the selected image using Pillow
    return download_image(image_path)

def show_popup(weather_data, forecast_data):

    global current_theme
    current_theme = light_mode_colors

    is_dark_mode_container = [False]
    

    # Create a new tkinter window
    root = tk.Tk()
    root.withdraw()  # Hide the main window

    # Create a new window for the popup
    popup = tk.Toplevel()
    popup.title("Weather App")
    #popup.overrideredirect(True)  # Remove window borders and title bar
    popup.wm_attributes("-topmost", True)  # Keep the window on top
    #popup.geometry("+100+5")  # Set the popup's position
    popup.geometry("800x900")
    # Set transparency (Windows: make a specific color transparent)
    # popup.wm_attributes("-alpha", 0)
    
    # Set transparency (macOS: make the entire window transparent)
    # popup.wm_attributes("-transparent", True)

    current_theme = tk.StringVar(value="Default")


    def update_image_based_on_theme(theme):
        weather_image = get_image_based_on_weather(weather_data, theme)
        if weather_image.format == 'GIF':
            frames = [ImageTk.PhotoImage(frame.copy().resize((300,300), Image.LANCZOS)) for frame in ImageSequence.Iterator(weather_image)]
            delay = weather_image.info.get('duration', 100)
            animate_gif(image_label, frames, delay)
        else:
            weather_image_tk = ImageTk.PhotoImage(weather_image)
            image_label.config(image=weather_image_tk)
            image_label.image = weather_image_tk

    def on_theme_change(*args):
        """Callback when the theme is changed."""
        update_image_based_on_theme(current_theme.get())

    current_theme.trace_add("write", on_theme_change)

    
    # Create a message to show in the popup
    message = (f"City: {weather_data['name']}\n"
               f"Current Temperature: {weather_data['main']['temp']:.1f}°F\n"
               f"Weather: {weather_data['weather'][0]['description']}")

    message_label = tk.Label(popup, text=message, padx=5, pady=5, fg="black")
    message_label.pack()    
        
    # Get the image based on weather conditions
    weather_image = get_image_based_on_weather(weather_data)
    #resize image might need to use if we use a different pictures
    #resized_weather_image = weather_image.resize((100,100), Image.LANCZOS)
    if weather_image.format == 'GIF':
        frames = [ImageTk.PhotoImage(frame.copy().resize((300,300), Image.LANCZOS)) for frame in ImageSequence.Iterator(weather_image)]
        weather_image_tk = frames[0]
        delay = weather_image.info.get('duration', 100)
        image_label = tk.Label(popup, image=weather_image_tk)
        image_label.pack()
        animate_gif(image_label, frames, delay)
    else:
        weather_image_tk = ImageTk.PhotoImage(weather_image)
        image_label = tk.Label(popup, image=weather_image_tk)
        image_label.image = weather_image_tk
        image_label.pack()

    #resize image might need to use if we use a different pictures
   # resized_weather_image = weather_image.resize((400,400), Image.LANCZOS)
    
    # Create a Tkinter-compatible photo image
    #weather_image_tk = ImageTk.PhotoImage(weather_image)

    # Create a label for the message with a transparent background
    #message_label = tk.Label(popup, text=message, padx=10, pady=10, fg="black")
    #message_label.pack()

    # Create a label for the image with a transparent background
   # image_label = tk.Label(popup, image=weather_image_tk)
    #image_label.image = weather_image_tk  # Keep a reference to avoid garbage collection
    #image_label.pack()

     # Show the forecast
    forecast_label = tk.Label(popup, text="5-Day Forecast:", padx=5, pady=10, fg="black", font=("Helvetica", 10, "bold"))
    forecast_label.pack()

    # Format and display forecast for 5 days
    forecast_data = format_forecast(forecast_data)
    for day_forecast in forecast_data:
        forecast_day_label = tk.Label(popup, text=day_forecast, padx=5, pady=5, fg="black")
        forecast_day_label.pack()

    # Ensure the popup window updates its layout to accommodate the image
    #popup.update_idletasks()  # Forces the window to update its size after adding widgets

    themes = ["Default", "Rainy", "Sunny", "Snowy"]
    theme_menu = tk.OptionMenu(popup, current_theme, *themes)
    theme_menu.pack(pady=10)    
    
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

def setup_weather_app():

    global current_theme
    current_theme = light_mode_colors  # Default theme is light
    
    # Mutable container to track dark mode status
    is_dark_mode_container = [False]

    root = tk.Tk()
    root.title("Weather App")
    root.geometry("500x600")

    global typed_location_entry

    #show default weather image
    weather_image = download_image(LOGO_PATH)

    if weather_image.format == 'GIF':
        frames = [ImageTk.PhotoImage(frame.copy().resize((300, 300), Image.LANCZOS))
        for frame in ImageSequence.Iterator(weather_image)]
        
        weather_image_tk = frames[0]
        delay = weather_image.info.get('duration', 100)
        image_label = tk.Label(root, image=weather_image_tk)
        image_label.pack(padx=5)
        animate_gif(image_label, frames, delay)
    else:
        weather_image_tk = ImageTk.PhotoImage(weather_image)
        image_label = tk.Label(root, image=weather_image_tk)
        image_label.image = weather_image_tk
        image_label.pack(padx=5)
    
    tk.Button(root, text="Current Location Weather", font=('Times', 18), command=show_current_location_weather).pack(padx=5)

    tk.Label(root, text="Type in City: ", font=('Times', 18)).pack(padx=5)
    typed_location_entry = tk.Entry(root, width=10, font=('Times', 18))
    typed_location_entry.pack()

    tk.Button(root, text="Get City Weather", font=('Times', 18), command=show_typed_location_weather).pack(pady=10)

     # Toggle Button
    toggle_button = tk.Button(
        root,
        text="Toggle Dark Mode",
        command=lambda: toggle_mode(root, is_dark_mode_container)
    )
    toggle_button.pack(pady=5)
    
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


