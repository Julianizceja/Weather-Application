import requests
from PIL import Image, ImageSequence
import io

# Paths to your custom .gif images
Pokemon_A_PATH = 'https://i.pinimg.com/originals/67/93/45/679345808c0a740e7aec8ff270192d23.gif'  # Hot weather GIF
Pokemon_B_PATH = 'https://media.tenor.com/EzU33OqujNsAAAAi/glaceon-eevee.gif'  # Cool weather GIF
Pokemon_C_PATH = 'https://www.shinyhunters.com/images/regular/134.gif'  # Rainy weather GIF
IMAGE_SNOWY_PATH = ''  # Snowy weather image (optional)
Import_A_PATH = ''
Import_B_PATH = ''
Import_C_PATH = ''


def download_image(image_url):
    response = requests.get(image_url)
    if response.status_code == 200:
        image_data = io.BytesIO(response.content)
        return Image.open(image_data)  # Use Pillow to open the image
    else:
        return None


def get_image_based_on_weather(weather_data, theme="Default"):
    temperature = weather_data['main']['temp']
    weather_description = weather_data['weather'][0]['description'].lower()

    # Theme-based image selection
    if theme == "Rainy":
        image_path = Pokemon_C_PATH
    elif theme == "Sunny":
        image_path = Pokemon_A_PATH
    elif theme == "Snowy":
        image_path = IMAGE_SNOWY_PATH
    else:
        # Default behavior
        if 'rain' in weather_description:
            image_path = Pokemon_C_PATH
        elif temperature >= 80:
            image_path = Pokemon_A_PATH
        elif temperature <= 70:
            image_path = Pokemon_B_PATH
        else:
            image_path = Pokemon_A_PATH

    return download_image(image_path)
