from yandex_cloud_ml_sdk import YCloudML
import json
import aiohttp
from types import TracebackType
from typing import Any, Dict, List, Optional, Type, Union


from config import SYSTEM_FOLDER_ID, SERVICE_SECRET_KEY
from api_interface import *


class API(APIInterface):
    """
    Asynchronous client for interacting with the Yandex (YCloudML) API.
    
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
        self.sdk = YCloudML(
            folder_id=SYSTEM_FOLDER_ID,
            auth=SERVICE_SECRET_KEY,
        )
        self.model = self.sdk.models.image_generation("yandex-art")
        self.model = self.model.configure(width_ratio=2, height_ratio=1)
        self.pending_images = []
        self.ready_images = []

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
        if not prompt:
            raise WrongParametersError("No prompt")
        message = prompt
        try:
            operation = self.model.run_deferred(message)
        except Exception as e:
            raise ImageGenerationError("Unexpected failure") from e
        self.pending_images.append(operation)

    async def checkGeneration(self) -> None:
        """
        Check status of pending image generations.
        
        Raises:
            IncorrectUseError: If credentials are missing
            WrongResponseBodyError: For invalid response format
            ImageGenerationError: For failed generations
        """
        for index, operation in enumerate(self.pending_images):
            if operation.get_status().is_running:
                continue
            if operation.get_status().is_succeeded:
                result = operation.get_result()
                self.ready_images.append(result.image_bytes)
                self.pending_images[index] = None
            else:
                raise ImageGenerationError("Server failure")
        self.pending_images = list(filter(lambda x: x is not None, self.pending_images))
