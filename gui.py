import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk, ImageSequence
import requests  # For OpenWeather API integration
import json
import os
import subprocess  # For opening weather.py
from io import BytesIO  # For handling image data from a URL
import geocoder  # To get current location

class WeatherApp(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Weather App")
        self.geometry("400x750")
        self.configure(bg="white")

        # Variables
        self.current_image = None
        self.gif_frames = None
        self.current_frame = 0
        self.saved_image_path = None
        self.weather_data = None
        self.api_key = "d22608d632cd6a389dc448f6d67a26c4"

        # UI Elements
        self.create_widgets()

    def create_widgets(self):
        """Set up all widgets in the GUI."""
        # Image Display
        self.image_label = tk.Label(self, bg="white")
        self.image_label.pack(pady=10)

        # Weather Info
        self.weather_frame = tk.Frame(self, bg="white")
        self.weather_frame.pack(pady=10)
        self.city_entry = tk.Entry(self.weather_frame, width=30)
        self.city_entry.pack(side="left", padx=5)
        tk.Button(self.weather_frame, text="Get Weather", command=self.get_weather).pack(side="left", padx=5)

        # Current Location Button
        tk.Button(self.weather_frame, text="Current Location", command=self.get_current_location_weather).pack(side="left", padx=5)

        # Frame for Save Data Button (Centered below the weather buttons)
        self.save_frame = tk.Frame(self, bg="white")
        self.save_frame.pack(pady=10)
        tk.Button(self.save_frame, text="Save Data", command=self.save_data).pack(side="left", padx=5)

        # Output label for displaying results
        self.output_label = tk.Label(self, text="", bg="white", wraplength=300, justify="left", anchor="w")
        self.output_label.pack(pady=20, fill="x", padx=10)


        # Import Buttons
        import_frame = tk.Frame(self, bg="white")
        import_frame.pack(pady=20)
        tk.Button(import_frame, text="Import Photo", command=self.import_photo).pack(side="left", padx=5)
        tk.Button(import_frame, text="Import GIF", command=self.import_gif).pack(side="left", padx=5)

        # Theme Selector
        self.theme_selector = tk.StringVar(value="Default")
        theme_dropdown = tk.OptionMenu(import_frame, self.theme_selector, "Default", "Pokemon", "Avatar")
        theme_dropdown.pack(side="left", padx=5)

        # Display Button (new)
        tk.Button(self, text="Display", command=self.display_weather).pack(pady=10)

        # Display startup image
        self.show_startup_image()

    def show_startup_image(self):
        """Display an animated startup GIF on app load."""
        try:
            startup_image_url = "https://i.gifer.com/KH8F.gif"  # URL to your startup image
            response = requests.get(startup_image_url)
            image_data = response.content
            startup_image = Image.open(BytesIO(image_data))
        
            # Extract frames from the GIF
            self.gif_frames = []
            for frame in ImageSequence.Iterator(startup_image):
                resized_frame = frame.copy().resize((250, 250), Image.LANCZOS)
                self.gif_frames.append(ImageTk.PhotoImage(resized_frame.convert("RGBA")))

            self.current_frame = 0  # Start with the first frame
            self.animate_startup_gif()  # Start animating the GIF
        except Exception as e:
            self.output_label.config(text=f"Error loading startup image: {e}")

    def animate_startup_gif(self):
        """Animate the startup GIF frames in a loop."""
        if self.gif_frames:
            self.image_label.config(image=self.gif_frames[self.current_frame])
            self.current_frame = (self.current_frame + 1) % len(self.gif_frames)
            self.after(100, self.animate_startup_gif)  # Repeat every 100ms for smooth animation

    def get_weather(self):
        """Fetch weather data from OpenWeather API."""
        city = self.city_entry.get()
        if not city:
            self.output_label.config(text="Please enter a city.")
            return

        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={self.api_key}&units=imperial"
        try:
            response = requests.get(url)
            data = response.json()

            if data.get("cod") != 200:
                self.output_label.config(text=f"Error: {data.get('message', 'Unknown error')}")
                return

            weather = data["weather"][0]["description"]
            temp = data["main"]["temp"]
            feels_like = data["main"]["feels_like"]
            self.weather_data = {
                "city": city.capitalize(),
                "weather": weather.capitalize(),
                "temperature": temp,
                "feels_like": feels_like,
            }
            self.output_label.config(
                text=f"Weather in {city.capitalize()}:\n"
                     f"{weather.capitalize()}\n"
                     f"Temperature: {temp}°F\n"
                     f"Feels Like: {feels_like}°F"
            )
        except Exception as e:
            self.output_label.config(text=f"Error fetching weather: {e}")

    def get_current_location_weather(self):
        """Fetch weather data for the current location."""
        g = geocoder.ip('me')  # Get current location using IP address
        lat, lng = g.latlng

        if lat and lng:
            url = f"http://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lng}&appid={self.api_key}&units=imperial"
            try:
                response = requests.get(url)
                data = response.json()

                if data.get("cod") != 200:
                    self.output_label.config(text=f"Error: {data.get('message', 'Unknown error')}")
                    return

                weather = data["weather"][0]["description"]
                temp = data["main"]["temp"]
                feels_like = data["main"]["feels_like"]
                city = data["name"]
                self.weather_data = {
                    "city": city,
                    "weather": weather.capitalize(),
                    "temperature": temp,
                    "feels_like": feels_like,
                }
                self.output_label.config(
                    text=f"Weather in {city}:\n"
                         f"{weather.capitalize()}\n"
                         f"Temperature: {temp}°F\n"
                         f"Feels Like: {feels_like}°F"
                )
            except Exception as e:
                self.output_label.config(text=f"Error fetching weather: {e}")
        else:
            self.output_label.config(text="Unable to retrieve current location.")

    def display_image(self, file_path):
        """Display a static image in the image label."""
        try:
            # Clear the startup image when a new image is loaded
            self.image_label.config(image='')

            imported_image = Image.open(file_path)
            imported_image = imported_image.resize((250, 250), Image.LANCZOS)
            self.current_image = ImageTk.PhotoImage(imported_image)
            self.image_label.config(image=self.current_image)
            self.saved_image_path = file_path
            self.output_label.config(text=f"Image loaded: {file_path}")
        except Exception as e:
            self.output_label.config(text=f"Error displaying image: {e}")

    def display_gif(self, file_path):
        """Display an animated GIF in the GIF label."""
        try:
            # Clear the startup image when a new gif is loaded
            self.image_label.config(image='')

            gif_image = Image.open(file_path)
            self.gif_frames = []
            for frame in ImageSequence.Iterator(gif_image):
                resized_frame = frame.copy().resize((250, 250), Image.LANCZOS)
                self.gif_frames.append(ImageTk.PhotoImage(resized_frame.convert("RGBA")))
            self.current_frame = 0
            self.saved_image_path = file_path
            self.animate_gif()
            self.output_label.config(text=f"GIF loaded: {file_path}")
        except Exception as e:
            self.output_label.config(text=f"Error displaying GIF: {e}")

    def animate_gif(self):
        """Animate the GIF frames in a loop."""
        if self.gif_frames:
            self.image_label.config(image=self.gif_frames[self.current_frame])
            self.current_frame = (self.current_frame + 1) % len(self.gif_frames)
            self.after(100, self.animate_gif)

    def import_photo(self):
        """Handle importing a photo and displaying it."""
        file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg;*.jpeg;*.png")])
        if file_path:
            self.display_image(file_path)

    def import_gif(self):
        """Handle importing a GIF and displaying it."""
        file_path = filedialog.askopenfilename(filetypes=[("GIF files", "*.gif")])
        if file_path:
            self.display_gif(file_path)

    def save_data(self):
        """Save the image path and weather data to a file."""
        theme = self.theme_selector.get()  # Retrieve the selected theme from the dropdown

        # Check if theme is 'Default' and ensure both weather data and image/GIF are available
        if theme == "Default":
            if not self.weather_data:
                self.output_label.config(text="Please fetch weather data before saving for the 'Default' theme.")
                return
            if not self.saved_image_path:
                self.output_label.config(text="Please import an image or GIF before saving for the 'Default' theme.")
                return
    
        # If the theme is 'Pokemon', we need weather data
        if theme == "Pokemon" and not self.weather_data:
            self.output_label.config(text="Please fetch weather data before saving for the 'Pokemon' theme.")
            return

        # If the theme is 'Pokemon' and no image is loaded, it's allowed
        # If no image is loaded, we just save the weather data and theme
        data = {
            "weather_data": self.weather_data if self.weather_data else None,
            "theme": theme,
        }

        # If the theme is 'Avatar', we need weather data
        if theme == "Avatar" and not self.weather_data:
            self.output_label.config(text="Please fetch weather data before saving for the 'Avatar' theme.")
            return

        # If the theme is 'Avatar' and no image is loaded, it's allowed
        # If no image is loaded, we just save the weather data and theme
        data = {
            "weather_data": self.weather_data if self.weather_data else None,
            "theme": theme,
        }

        # If an image is loaded, include it in the saved data
        if self.saved_image_path:
            data["image_path"] = self.saved_image_path
    
        with open("saved_data.json", "w") as f:
            json.dump(data, f)
    
        self.output_label.config(text="Data saved successfully.")


    def display_weather(self):
        """Close the current window and open weather.py."""
        self.destroy()  # Close current window
        subprocess.run(["python", "weather.py"])  # Open weather.py


if __name__ == "__main__":
    app = WeatherApp()
    app.mainloop()
