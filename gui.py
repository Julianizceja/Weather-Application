import tkinter as tk
from tkinter import filedialog, ttk
from PIL import Image, ImageTk
from datetime import datetime
import requests
import geocoder
from io import BytesIO
import os
import subprocess  # Import subprocess to run the script

API_KEY = 'd22608d632cd6a389dc448f6d67a26c4'
BASE_URL = 'https://api.openweathermap.org/data/2.5/weather'


def get_weather_by_city(city):
    """Fetch weather data for a specific city."""
    params = {
        'q': city,
        'appid': API_KEY,
        'units': 'imperial'  # Fahrenheit
    }
    response = requests.get(BASE_URL, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        return None


def get_weather_by_coords(lat, lon):
    """Fetch weather data based on coordinates."""
    params = {
        'lat': lat,
        'lon': lon,
        'appid': API_KEY,
        'units': 'imperial'  # Fahrenheit
    }
    response = requests.get(BASE_URL, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        return None


class WeatherApp(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Weather App")
        self.geometry("400x600")
        self.configure(bg="white")

        # Variables
        self.show_time = tk.BooleanVar(value=True)
        self.theme = tk.StringVar(value="Default")
        self.current_image = None
        self.current_location = ""  # For storing the current location
        self.imported_files = []  # Stores paths of imported images/GIFs

        # References to buttons for updating text
        self.cold_button = None
        self.warm_button = None
        self.severe_button = None

        # UI Elements
        self.create_widgets()

    def create_widgets(self):
        """Set up all widgets in the GUI."""

        # Top image
        self.image_label = tk.Label(self, bg="white")
        self.image_label.pack(pady=10)
        self.load_default_image()

        # Location Entry
        location_frame = tk.Frame(self, bg="white")
        location_frame.pack(pady=10)

        tk.Label(location_frame, text="Enter Location:", bg="white").pack(side="left", padx=5)
        self.location_entry = tk.Entry(location_frame, width=20)
        self.location_entry.pack(side="left", padx=5)
        tk.Button(location_frame, text="Get Weather", command=self.fetch_weather).pack(side="left", padx=5)

        # Button to display current location weather
        tk.Button(self, text="Show Current Location Weather", command=self.display_current_location_weather).pack(pady=5)

        # Toggle Options
        options_frame = tk.Frame(self, bg="white")
        options_frame.pack(pady=10)

        tk.Checkbutton(options_frame, text="Display Time", variable=self.show_time, bg="white",
                       command=self.toggle_time_display).pack(anchor="w")

        # Import Options
        import_frame = tk.Frame(self, bg="white")
        import_frame.pack(pady=10)

        self.cold_button = tk.Button(import_frame, text="Cold Import", command=self.import_photo)
        self.cold_button.pack(side="left", padx=5)

        self.warm_button = tk.Button(import_frame, text="Warm Import", command=self.import_gif)
        self.warm_button.pack(side="left", padx=5)

        self.severe_button = tk.Button(import_frame, text="Severe Import", command=self.import_weather_icon)
        self.severe_button.pack(side="left", padx=5)

        # Theme Selector
        theme_frame = tk.Frame(self, bg="white")
        theme_frame.pack(pady=10)

        tk.Label(theme_frame, text="Select Theme:", bg="white").pack(side="left", padx=5)
        themes = ["Default", "Rainy", "Sunny", "Snowy"]
        self.theme_selector = ttk.Combobox(theme_frame, values=themes, textvariable=self.theme)
        self.theme_selector.pack(side="left", padx=5)

        # Bind theme change handler
        self.theme.trace("w", self.handle_theme_change)

        # Submit Button positioned below the theme selector
        tk.Button(self, text="Submit", command=self.run_weather_script).pack(pady=10)

        # Output Area
        self.output_label = tk.Label(self, text="", bg="white", wraplength=300, justify="left")
        self.output_label.pack(pady=20)

        # Time Display
        self.time_label = tk.Label(self, text="", bg="white", font=("Arial", 10))
        self.time_label.pack(pady=5)
        if self.show_time.get():
            self.update_time()

    def load_default_image(self):
        """Load a default image at startup."""
        try:
            url = "https://www.freeiconspng.com/thumbs/weather-icon-png/weather-icon-png-2.png"
            response = requests.get(url)
            img_data = response.content
            default_image = Image.open(BytesIO(img_data))
            self.current_image = ImageTk.PhotoImage(default_image)
            self.image_label.config(image=self.current_image)
        except Exception as e:
            self.image_label.config(text="No Image Found", bg="gray")
            self.output_label.config(text=f"Error loading default image: {e}")

    def import_image(self, filetypes, button):
        """Generic method to handle importing an image and updating button text."""
        try:
            file_path = filedialog.askopenfilename(filetypes=filetypes)
            if not file_path:
                self.output_label.config(text="No file selected.")
                return

            imported_image = Image.open(file_path)
            self.current_image = ImageTk.PhotoImage(imported_image)
            self.image_label.config(image=self.current_image)

            button.config(text="✔️ Import Successful")

            if file_path not in self.imported_files:
                self.imported_files.append(file_path)

            self.update_theme_selector()

        except Exception as e:
            self.output_label.config(text=f"Error importing image: {e}")
            button.config(text="❌ Import Failed")

    def import_photo(self):
        self.import_image(filetypes=[("image", "*.jpg;*.jpeg;*.png;*.gif")], button=self.cold_button)

    def import_gif(self):
        self.import_image(filetypes=[("image", "*.jpg;*.jpeg;*.png;*.gif")], button=self.warm_button)

    def import_weather_icon(self):
        self.import_image(filetypes=[("image", "*.jpg;*.jpeg;*.png;*.gif")], button=self.severe_button)

    def update_theme_selector(self):
        themes = ["Default", "Rainy", "Sunny", "Snowy"]
        if self.imported_files:
            themes.append("My Imports")
        self.theme_selector['values'] = themes
        if "My Imports" in themes:
            self.theme.set("My Imports")

    def handle_theme_change(self, *args):
        selected_theme = self.theme.get()
        if selected_theme == "My Imports" and self.imported_files:
            try:
                imported_image = Image.open(self.imported_files[-1])
                imported_image = imported_image.resize((350, 150), Image.ANTIALIAS)
                self.current_image = ImageTk.PhotoImage(imported_image)
                self.image_label.config(image=self.current_image)
            except Exception as e:
                self.output_label.config(text=f"Error loading imported image: {e}")
        elif selected_theme == "Default":
            self.load_default_image()
        else:
            self.output_label.config(text=f"Selected theme: {selected_theme}")

    def fetch_weather(self):
        location = self.location_entry.get().strip()
        if not location:
            self.output_label.config(text="Please enter a location.")
            return

        weather_data = get_weather_by_city(location)
        if weather_data:
            weather_text = (f"City: {weather_data['name']}\n"
                            f"Temperature: {weather_data['main']['temp']}°F\n"
                            f"Weather: {weather_data['weather'][0]['description']}")
            self.output_label.config(text=weather_text)
        else:
            self.output_label.config(text="Could not retrieve weather data.")

    def display_current_location_weather(self):
        g = geocoder.ip('me')
        if g.latlng:
            lat, lon = g.latlng
            location = f"Latitude: {lat}, Longitude: {lon}"
            weather_data = get_weather_by_coords(lat, lon)

            if weather_data:
                weather_text = (f"Location: {location}\n"
                                f"Temperature: {weather_data['main']['temp']}°F\n"
                                f"Weather: {weather_data['weather'][0]['description']}")
                self.output_label.config(text=weather_text)
            else:
                self.output_label.config(text="Could not retrieve weather data for current location.")
        else:
            self.output_label.config(text="Could not determine your current location.")

    def toggle_time_display(self):
        if self.show_time.get():
            self.update_time()
        else:
            self.time_label.config(text="")

    def update_time(self):
        if self.show_time.get():
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.time_label.config(text=f"Current Time: {now}")
            self.after(1000, self.update_time)

    def run_weather_script(self):
        try:
            # This will run the weather.py script
            self.destroy()
            os.system("python weather.py")
        except subprocess.CalledProcessError as e:
            self.output_label.config(text=f"Error running weather script: {e}")


if __name__ == "__main__":
    app = WeatherApp()
    app.mainloop()
