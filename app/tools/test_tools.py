from langchain.tools import BaseTool
from math import pi
from typing import Union, Any

class WeaApiTool(BaseTool):

    name = 'weather_api'
    description = 'query_weather'
    verbose = True

    def _run(self, *args: Any, **kwargs: Any):
        #I can only get ('New York ') here, but I want to get' What is the weather like right now in New York '  what should I do ?
        print(args)
        print(kwargs)
        return 'good'

class CircumferenceTool(BaseTool):
    name = "Circumference"
    description = "Use this tool to calculate the circumference of a circle."

    def _run(self, query: str) -> Union[int, float]:
        try:
            radius = float(query)
            return 2 * pi * radius
        except ValueError:
            return "Invalid input. Please provide a valid radius."

    async def _arun(self, query: str) -> Union[str, bool]:
        raise NotImplementedError("tool does not support async")