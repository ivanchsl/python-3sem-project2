import json
import base64
import aiohttp
from types import TracebackType
from typing import Any, Dict, List, Optional, Type, Union


class APIError(Exception):
    """
    Base exception for API errors
    """


class IncorrectUseError(APIError):
    """
    Exception if the API is used incorrectly
    """


class WrongParametersError(APIError):
    """
    Exception if user gave wrong parameters
    """


class FailedRequestError(APIError):
    """
    Exception if request status is incorrect
    """


class WrongResponseBodyError(APIError):
    """
    Exception if request body is unexpected
    """


class ImageGenerationError(APIError):
    """
    Exception if server did not generate an image
    """


class APIInterface:
    """
    Asynchronous client for interacting with the API.
    
    Args:
        api_key: Optional API key for authentication
        secret_key: Optional secret key for authentication
        session: Optional existing aiohttp client session to reuse
    """

    def __init__(
        self,
        api_key: str = None,
        secret_key: str = None,
        session: Optional[aiohttp.ClientSession] = None
    ) -> None:
        raise SyntaxError("You did not choose an API") 

    async def __aenter__(self):
        """
        Asynchronous context manager entry point.
        """
        return self

    async def __aexit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[TracebackType]
    ) -> None:
        """
        Asynchronous context manager exit point.
        
        Args:
            exc_type: Exception type if an exception occurred
            exc_val: Exception instance if an exception occurred
            exc_tb: Traceback if an exception occurred
        """

    async def startGeneration(
        self,
        prompt: str,
        style: str
    ) -> None:
        """
        Start a new image generation process.
        
        Args:
            prompt: Text prompt for image generation
            style: Style name for image generation
            
        Raises:
            SyntaxError: You have to choose an API
        """
        raise SyntaxError("You did not choose an API") 

    async def checkGeneration(self) -> None:
        """
        Check status of pending image generations.
        
        Raises:
            SyntaxError: You have to choose an API
        """
        raise SyntaxError("You did not choose an API")

    def getPhotos(self) -> List[str]:
        """
        Retrieve and clear the list of generated images.
        
        Returns:
            list[str]: List of generated images
        """
        images = self.ready_images
        self.ready_images = []
        return images

    async def _getStyles(self) -> List[Dict[str, str]]:
        """
        Fetch available styles from the API.
        
        Returns:
            list[dict]: List of style dictionaries with title and display name
            
        Raises:
            WrongResponseBodyError: For invalid response format
        """
        return [{
            "title": "Basic",
            "display_name": "basic"
        }]

    async def getStyleList(self):
        """
        Get the list of available style titles.
        
        Returns:
            list[str]: List of available style titles
        """
        data = await self._getStyles()
        return list(map(lambda x : x["title"], data))

    async def getStyleByTitle(
        self,
        title: str
    ) -> str:
        """
        Get a style display name by its title.
        
        Args:
            title: Style title to look up
            
        Returns:
            str: Style display name
            
        Raises:
            WrongParametersError: If style is not found
        """
        data = await self._getStyles()
        for elem in data:
            if elem["title"] == title:
                return elem["display_name"]
        raise WrongParametersError("Incorrect style")
