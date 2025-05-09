import json
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


class API:
    """
    Asynchronous client for interacting with the FusionBrain (Kandinsky) API.
    
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
        self.URL: str = "https://api-key.fusionbrain.ai/"
        self.AUTH_HEADERS: Dict[str, str] = ({
            "X-Key": f"Key {api_key}",
            "X-Secret": f"Secret {secret_key}",
        } if (api_key and secret_key) else {})
        self.session: Optional[aiohttp.ClientSession] = session
        self.session_closing: bool = False
        self.pending_images: List[Optional[str]] = []
        self.ready_images: List[str] = []

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
        if self.session_closing and not self.session.closed:
            await self.session.close()

    def _getSession(self) -> aiohttp.ClientSession:
        """
        Get a client session, creating it if needed.
        
        Returns:
            aiohttp.ClientSession: Active client session
            
        Raises:
            APIError: If session creation fails
        """
        if self.session is None or self.session.closed:
            try:
                self.session = aiohttp.ClientSession()
            except Exception as e:
                raise APIError("Unexpected exception") from e
            self.session_closing = True
        return self.session

    async def _handleRequest(
        self,
        method: str,
        required_status: int,
        *args: Any,
        **kwargs: Any
    ) -> Union[List[Any], Dict[str, Any]]:
        """
        Handle HTTP requests with common errors handling.
        
        Args:
            method: HTTP method to use
            required_status: Expected HTTP status code
            *args: Positional arguments for the request
            **kwargs: Keyword arguments for the request
            
        Returns:
            Optional[list, dict]: Parsed JSON response
            
        Raises:
            FailedRequestError: For request failures or invalid responses
            APIError: For unexpected errors
        """
        try:
            async with self._getSession().request(method, *args, **kwargs) as response:
                if response.status != required_status:
                    raise FailedRequestError(f"Wrong response status: {response.status}")
                data = await response.json()
        except (aiohttp.ClientError, json.JSONDecodeError) as e:
            raise FailedRequestError("Unable to complete the request") from e
        except FailedRequestError:
            raise
        except Exception as e:
            raise APIError("Unexpected exception") from e
        return data

    async def _handleGet(
        self,
        required_status: int,
        *args: Any,
        **kwargs: Any
    ) -> Union[List[Any], Dict[str, Any]]:
        """
        Handle GET requests with common errors handling.
        
        Args:
            required_status: Expected HTTP status code
            *args: Positional arguments for the request
            **kwargs: Keyword arguments for the request
            
        Returns:
            Optional[list, dict]: Parsed JSON response
        """
        return await self._handleRequest("GET", required_status, *args, **kwargs)

    async def _handlePost(
        self,
        required_status: int,
        *args: Any,
        **kwargs: Any
    ) -> Union[List[Any], Dict[str, Any]]:
        """
        Handle POST requests with common errors handling.
        
        Args:
            required_status: Expected HTTP status code
            *args: Positional arguments for the request
            **kwargs: Keyword arguments for the request
            
        Returns:
            Optional[list, dict]: Parsed JSON response
        """
        return await self._handleRequest("POST", required_status, *args, **kwargs)

    async def getModel(self) -> str:
        """
        Get the first available model ID.
        
        Returns:
            str: Model ID
            
        Raises:
            IncorrectUseError: If credentials are missing
            WrongResponseBodyError: For invalid response format
        """
        models_url = self.URL + "key/api/v1/pipelines"
        if not self.AUTH_HEADERS:
            raise IncorrectUseError("User did not provide credentials")
        data = await self._handleGet(200, models_url, headers=self.AUTH_HEADERS)

        if not isinstance(data, list) or len(data) < 1:
            raise WrongResponseBodyError("No models in the response")
        model = data[0]
        if not isinstance(model, dict):
            raise WrongResponseBodyError("Model structure is incorrect")
        model_id = model.get("id", None)
        if not model_id:
            raise WrongResponseBodyError("Model does not contain an id")
        return model_id

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
            IncorrectUseError: If credentials are missing
            WrongParametersError: For invalid parameters
            ImageGenerationError: For failed generation start
            WrongResponseBodyError: For invalid response format
        """
        if not self.AUTH_HEADERS:
            raise IncorrectUseError("User did not provide credentials")
        if not prompt or not style:
            raise WrongParametersError("Wrong parameters")
        params = {
            "type": "GENERATE",
            "style": style,
            "numImages": 1,
            "width": 1024,
            "height": 1024,
            "generateParams": {
                "query": prompt
            }
        }
        model = await self.getModel()
        start_url = self.URL + "key/api/v1/pipeline/run"
        form_data = aiohttp.FormData()
        form_data.add_field("pipeline_id", model)
        form_data.add_field("params", json.dumps(params), content_type="application/json")
        data = await self._handlePost(201, start_url, headers=self.AUTH_HEADERS, data=form_data)

        if not isinstance(data, dict):
            raise WrongResponseBodyError("Response body is incorrect")
        request_id = data.get("uuid", None)
        if not request_id:  
            raise ImageGenerationError("Response does contain an id")
        self.pending_images.append(request_id)

    async def checkGeneration(self) -> None:
        """
        Check status of pending image generations.
        
        Raises:
            IncorrectUseError: If credentials are missing
            WrongResponseBodyError: For invalid response format
            ImageGenerationError: For failed generations
        """
        if not self.AUTH_HEADERS:
            raise IncorrectUseError("User did not provide credentials")
        for index, request_id in enumerate(self.pending_images):
            if not request_id:
                continue
            check_url = self.URL + "key/api/v1/pipeline/status/" + request_id
            data = await self._handleGet(200, check_url, headers=self.AUTH_HEADERS)

            if not isinstance(data, dict):
                raise WrongResponseBodyError("Response body is incorrect")
            image_status = data.get("status", None)
            if not image_status:
                raise WrongResponseBodyError("Response does not contain a status")

            if image_status in ("INITIAL", "PROCESSING"):
                continue
            elif image_status == "DONE":
                result_dict = data.get("result", None)
                if not result_dict:
                    raise WrongResponseBodyError("Success response does not contain a result")
                result_images = result_dict.get("files", None)
                if not isinstance(result_images, list) or len(result_images) < 1:
                    raise WrongResponseBodyError("Success response does not contain any images")
                self.ready_images.append(result_images[0])
                self.pending_images[index] = None
            elif image_status == "FAIL":
                raise ImageGenerationError("Server failure")
            else:
                raise WrongResponseBodyError("Unexpected generation status")
        self.pending_images = list(filter(lambda x: x is not None, self.pending_images))

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
        data = await self._handleGet(200, "https://cdn.fusionbrain.ai/static/styles/key")
        if not isinstance(data, list) or len(data) < 1:
            raise WrongResponseBodyError("No styles in the response")
        try:
            return [{
                "title": elem["titleEn"],
                "display_name": elem["name"]
            } for elem in data]
        except KeyError as e:
            raise WrongResponseBodyError("Style is not properly named") from e

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
