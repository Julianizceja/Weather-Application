import tkinter as tk
from PIL import Image, ImageTk, ImageSequence
import json
import requests
import io
from urllib.parse import urlparse

# Pokemon GIF URLs based on weather conditions
Pokemon_A_PATH = 'https://i.pinimg.com/originals/67/93/45/679345808c0a740e7aec8ff270192d23.gif'  # Hot weather GIF temp 76 or more
Pokemon_B_PATH = 'https://media.tenor.com/EzU33OqujNsAAAAi/glaceon-eevee.gif'  # Cool weather GIF temp 70 or less
Pokemon_C_PATH = 'https://www.shinyhunters.com/images/regular/134.gif'  # Rainy weather GIF temperature says Raining
Pokemon_D_PATH = 'https://projectpokemon.org/home/uploads/monthly_2018_05/large.5aec4287c9aee_EeveeGif.gif.1687bde4b30e4ce1dd93c67f4bd13d24.gif'  # temp between 71-75
Avatar_A_PATH = 'https://static.wikia.nocookie.net/villains/images/2/23/Principe_zuko_by_yuzumi2000-d6lbrj4.png'
Avatar_B_PATH = 'https://static.wikia.nocookie.net/all-worlds-alliance/images/f/fb/Katara.png'
Avatar_C_PATH = 'https://static.wikia.nocookie.net/all-worlds-alliance/images/6/6a/Korra567.png'
Avatar_D_PATH = 'https://wallpapers.com/images/hd/avatar-aang-headshot-s6vbak3n7zd3732j.png'

class DisplayDataApp(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Display Data")
        self.overrideredirect(True)
        self.geometry("+100+100")
        self.wm_attributes("-alpha", 0.9)
        self.wm_attributes("-topmost", 1)
        self.configure(bg="white")

        # Track X and Y offset for dragging
        self.offset_x = tk.IntVar(value=0)
        self.offset_y = tk.IntVar(value=0)

        self.gif_frames = None
        self.current_frame = 0

        # UI Elements
        self.create_widgets()

        # Bind mouse events for dragging
        self.bind("<ButtonPress-1>", self.start_drag)
        self.bind("<B1-Motion>", self.perform_drag)

    def create_widgets(self):
        """Load and display saved data."""
        try:
            with open("saved_data.json", "r") as f:
                data = json.load(f)
        except FileNotFoundError:
            tk.Label(self, text="No saved data found.", bg="white").pack(pady=20)
            return

        # Check the theme and temperature
        theme = data.get("theme", "Default")
        weather_data = data["weather_data"]
        temperature = weather_data["temperature"]

        # Determine which Pokémon-themed GIF to display based on temperature or weather condition
        if theme == "Pokemon":
            if "rain" in weather_data["weather"].lower():  # If the weather description contains "rain"
                self.display_gif(Pokemon_C_PATH)  # Rainy weather
            elif temperature >= 76:
                self.display_gif(Pokemon_A_PATH)  # Hot weather
            elif temperature <= 70:
                self.display_gif(Pokemon_B_PATH)  # Cool weather
            elif 71 <= temperature <= 75:
                self.display_gif(Pokemon_D_PATH)  # Moderate temperature
        elif theme == "Avatar":
            if "rain" in weather_data["weather"].lower():  # If the weather description contains "rain"
                self.display_static_image(Avatar_C_PATH)  # Rainy weather
            elif temperature >= 76:
                self.display_static_image(Avatar_A_PATH)  # Hot weather
            elif temperature <= 70:
                self.display_static_image(Avatar_B_PATH)  # Cool weather
            elif 71 <= temperature <= 75:
                self.display_static_image(Avatar_D_PATH)  # Moderate temperature
        else:  # If theme is Default
            image_path = data["image_path"]
            try:
                if image_path.lower().endswith(".gif"):
                    self.display_gif(image_path)
                else:
                    self.display_static_image(image_path)
            except Exception as e:
                tk.Label(self, text=f"Error loading image: {e}", bg="white").pack(pady=20)

        # Display Weather Data
        weather_text = (
            f"City: {weather_data['city']}\n"
            f"Weather: {weather_data['weather']}\n"
            f"Temperature: {weather_data['temperature']}°F\n"
            f"Feels Like: {weather_data['feels_like']}°F"
        )
        tk.Label(self, text=weather_text, bg="white", justify="left", font=("Arial", 14)).pack(side="left", padx=10)

        # Close Button
        close_button = tk.Button(self, text="Close", command=lambda: [self.destroy()])
        close_button.pack(side="bottom", pady=20, anchor="center")

    def display_static_image(self, file_path):
        """Display a static image, either from a URL or a local file path."""
        try:
            # Check if the path is a URL
            parsed_url = urlparse(file_path)
            if parsed_url.scheme in ('http', 'https'):
                # Fetch image from the URL
                response = requests.get(file_path)
                response.raise_for_status()  # Raise an error for bad responses (4xx, 5xx)
                img = Image.open(io.BytesIO(response.content))
            else:
                # Load image from local file path
                img = Image.open(file_path)
            
            # Resize the image to fit in the UI
            img = img.resize((150, 150), Image.LANCZOS)
            img = ImageTk.PhotoImage(img)
            
            # Display the image in a label
            image_label = tk.Label(self, image=img, bg="white")
            image_label.image = img  # Keep a reference to the image
            image_label.pack(side="left", padx=10)
            
        except Exception as e:
            tk.Label(self, text=f"Error loading image: {e}", bg="white").pack(pady=20)

    def display_gif(self, file_path):
        """Display an animated GIF from a URL or local file path."""
        try:
            # Check if the path is a valid URL
            parsed_url = urlparse(file_path)
            if parsed_url.scheme in ('http', 'https'):
                # Fetch GIF from the URL
                response = requests.get(file_path)
                response.raise_for_status()
                gif_image = Image.open(io.BytesIO(response.content))
            else:
                # Load GIF from local file path
                gif_image = Image.open(file_path)
        except Exception as e:
            tk.Label(self, text=f"Error loading GIF: {e}", bg="white").pack(pady=20)
            return

        self.gif_frames = []
        for frame in ImageSequence.Iterator(gif_image):
            resized_frame = frame.copy().resize((150, 150), Image.LANCZOS)
            self.gif_frames.append(ImageTk.PhotoImage(resized_frame.convert("RGBA")))

        self.image_label = tk.Label(self, bg="white")
        self.image_label.pack(side="left", padx=10)
        self.animate_gif()

    def animate_gif(self):
        """Animate the GIF frames in a loop."""
        if self.gif_frames:
            self.image_label.config(image=self.gif_frames[self.current_frame])
            self.current_frame = (self.current_frame + 1) % len(self.gif_frames)
            self.after(100, self.animate_gif)  # Adjust delay for smoother or faster playback

    def start_drag(self, event):
        """Capture initial mouse position when the user starts dragging."""
        self.offset_x.set(event.x)
        self.offset_y.set(event.y)

    def perform_drag(self, event):
        """Update window position while dragging."""
        x = self.winfo_x() + (event.x - self.offset_x.get())
        y = self.winfo_y() + (event.y - self.offset_y.get())
        self.geometry(f"+{x}+{y}")


if __name__ == "__main__":
    app = DisplayDataApp()
    app.mainloop()
