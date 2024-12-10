# Weather-Application
This project is a GUI-based Weather App built with Python and the Tkinter library. The application fetches current weather data and forecasts for a specified location or the user's current location, using the OpenWeather API. The app supports dynamic weather animations and includes a toggleable dark mode for an improved user experience.

Features

Current Weather: Fetch and display current weather data for the user's location or a manually entered location.

5-Day Forecast: View a 5-day weather forecast for the specified location.

Dynamic Weather Images: Displays weather-specific animations (e.g., GIFs) based on the current conditions.

Dark Mode: Option to toggle between light and dark themes.

Customizable Weather Images: Import custom images or animations for different weather conditions.

Requirements

To run this application, ensure you have the following installed:

Python 3.6 or newer

Required Python libraries:

requests

Pillow

geocoder

tkinter (comes pre-installed with Python)

geopy

You can install the required libraries with:

pip install requests Pillow geocoder geopy

Setup and Installation

Clone this repository or download the source code.

Install the required libraries using the command above.

Replace the placeholder API_KEY in the source code with your OpenWeather API key. You can obtain an API key by creating an account on the OpenWeather website.

Usage

Run the weather_app.py file using Python:

python weather_app.py

Use the app's GUI to:

View weather data for your current location.

Enter a city or city, state to fetch weather information.

Import custom weather animations or images.

Toggle between light and dark themes.

File Descriptions

weather_app.py: Main application file containing the logic and GUI.

Dynamic Weather Images: The app uses URLs for default animations. You can replace these with your custom images or animations by using the "Import Weather Image" button in the GUI.

API Endpoints

The application utilizes the following OpenWeather API endpoints:

Current Weather Data: https://api.openweathermap.org/data/2.5/weather

5-Day Forecast: https://api.openweathermap.org/data/2.5/forecast

Ensure that your API key has the appropriate access permissions for these endpoints.

Features Breakdown

Dynamic Animations: The app dynamically fetches and displays weather-specific animations. For example, a rainy GIF is shown for rain, a sunny GIF for clear skies, etc.

Dark and Light Modes: The theme toggle button lets users switch between dark and light modes for better accessibility.

Customizable Interface: Users can upload their own images or animations for specific weather conditions (e.g., hot, cold, rainy).

Limitations

Requires an active internet connection to fetch weather data.

The OpenWeather API key must be valid and have permissions for the used endpoints.

Future Improvements

Add hourly forecast visualization.

Add database where users can store their gifs and images

Allow Users to make accounts

Enhance the GUI design with additional customization options.

Add error handling for network connectivity issues.

License

This project is licensed under the MIT License. You are free to use, modify, and distribute this software, provided the original authorship is credited.
