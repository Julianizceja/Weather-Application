import requests
import geocoder
import tkinter as tk
from PIL import ImageTk, ImageSequence
from images import get_image_based_on_weather, download_image

API_KEY = 'd22608d632cd6a389dc448f6d67a26c4'
BASE_URL = 'https://api.openweathermap.org/data/2.5/weather'


def get_weather(lat, lon):
    params = {
        'lat': lat,
        'lon': lon,
        'appid': API_KEY,
        'units': 'imperial'  # Get temperature in Fahrenheit
    }
    response = requests.get(BASE_URL, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        return None


def animate_gif(label, frames, delay):
    def update(index):
        frame = frames[index]
        label.config(image=frame)
        label.image = frame  # Keep a reference to avoid garbage collection
        label.after(delay, update, (index + 1) % len(frames))

    update(0)


def show_popup(weather_data):
    root = tk.Tk()
    root.withdraw()

    popup = tk.Toplevel()
    popup.overrideredirect(True)  # Remove window decorations
    popup.wm_attributes("-topmost", True)  # Always on top
    popup.geometry("+100+100")
    popup.wm_attributes("-alpha", 0.9)  # Set transparency to 90%

    # Variables
    current_theme = tk.StringVar(value="Default")  # Track the selected theme
    offset_x = tk.IntVar(value=0)  # Track X offset for dragging
    offset_y = tk.IntVar(value=0)  # Track Y offset for dragging

    def start_drag(event):
        """Record the starting position for dragging."""
        offset_x.set(event.x)
        offset_y.set(event.y)

    def perform_drag(event):
        """Move the popup based on mouse dragging."""
        x = popup.winfo_x() + (event.x - offset_x.get())
        y = popup.winfo_y() + (event.y - offset_y.get())
        popup.geometry(f"+{x}+{y}")

    def update_image_based_on_theme(theme):
        """Update the displayed image based on the selected theme."""
        weather_image = get_image_based_on_weather(weather_data, theme)
        if weather_image.format == 'GIF':
            frames = [ImageTk.PhotoImage(frame.copy()) for frame in ImageSequence.Iterator(weather_image)]
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

    # Enable dragging on the popup
    popup.bind("<ButtonPress-1>", start_drag)
    popup.bind("<B1-Motion>", perform_drag)

    # Popup content
    message = (f"City: {weather_data['name']}\n"
               f"Temperature: {weather_data['main']['temp']}°F\n"
               f"Weather: {weather_data['weather'][0]['description']}")

    message_label = tk.Label(popup, text=message, padx=10, pady=10, fg="black")
    message_label.pack()

    # Initial weather image
    weather_image = get_image_based_on_weather(weather_data)
    if weather_image.format == 'GIF':
        frames = [ImageTk.PhotoImage(frame.copy()) for frame in ImageSequence.Iterator(weather_image)]
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

    # Theme dropdown
    themes = ["Default", "Rainy", "Sunny", "Snowy"]
    theme_menu = tk.OptionMenu(popup, current_theme, *themes)
    theme_menu.pack(pady=10)

    # Close button
    close_button = tk.Button(popup, text="Close", command=lambda: [popup.destroy(), root.quit()])
    close_button.pack(pady=10)

    root.mainloop()


# Geolocation
g = geocoder.ip('me')
lat, lon = g.latlng

weather_data = get_weather(lat, lon)

if weather_data:
    show_popup(weather_data)
else:
    show_popup({"name": "Error", "main": {"temp": ""}, "weather": [{"description": "Weather data not found!"}]})

