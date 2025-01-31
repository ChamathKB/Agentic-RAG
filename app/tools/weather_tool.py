from langchain.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Optional, Type
import requests
from app.configs import OPENWEATHER_API_KEY
from app.models.schema import GetCurrentWeatherCheckInput


def get_current_weather(location: str) -> str:
    """
    Get the current weather for a given location using OpenWeather API.
    
    Args:
        location (str): Name of the location to get weather for
        
    Returns:
        str: Weather information including temperature and description
        
    Raises:
        requests.exceptions.RequestException: If API request fails
    """
    url = f"https://api.openweathermap.org/data/2.5/weather?q={location}&appid={OPENWEATHER_API_KEY}"
    
    response = requests.get(url)
    data = response.json()
    temperature = data["main"]["temp"]
    description = data["weather"][0]["description"]
    return f"The temperature in {location} is {temperature}°C with {description}."


class WeatherTool(BaseTool):
    """Tool for getting current weather information for a location.
    
    Attributes:
        name (str): Name of the tool
        description (str): Description of what the tool does
        args_schema (Optional[Type[BaseModel]]): Schema for validating input arguments
    """
    name: str = "Weather"
    description: str = "useful for when you need to answer questions about the weather"

    def _run(self, location: str) -> str:
        """Get current weather for a location.
        
        Args:
            location (str): Name of location to get weather for
            
        Returns:
            str: Weather information including temperature and description
        """
        weather_response = get_current_weather(location)
        return weather_response

    def _arun(self, query: str) -> None:
        """Async version of run - not implemented.
        
        Args:
            query (str): Query string
            
        Raises:
            NotImplementedError: This tool does not support async operations
        """
        raise NotImplementedError("This tool does not support async")
    
    args_schema: Optional[Type[BaseModel]] = GetCurrentWeatherCheckInput
