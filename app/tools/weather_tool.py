from langchain.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Optional, Type
import requests
from app.configs import OPENWEATHER_API_KEY

def get_current_weather(location):
    
    url = f"https://api.openweathermap.org/data/2.5/weather?q={location}&appid={OPENWEATHER_API_KEY}"
    
    response = requests.get(url)
    data = response.json()
    temperature = data["main"]["temp"]
    description = data["weather"][0]["description"]
    return f"The temperature in {location} is {temperature}°C with {description}."


class GetCurrentWeatherCheckInput(BaseModel):
    # Check the input for Weather
    location: str = Field(..., description = "The name of the location name for which we need to find the weather")


class WeatherTool(BaseTool):
    name = "Weather"
    description = "useful for when you need to answer questions about the weather"


    def _run(self, location):
        weather_response = get_current_weather(location)
        return weather_response

    def _arun(self, query):
        raise NotImplementedError("This tool does not support async")
    
    args_schema: Optional[Type[BaseModel]] = GetCurrentWeatherCheckInput