"""This module provides the VllmApiResponse class."""


class VllmModel:
    """Represents a VLLM model."""

    def __init__(self, model_id: str) -> None:
        """Initialize the VllmModel object.

        Args:
            model_id (str): The model ID.

        """
        self.model_id = model_id


class VllmChatApiResponse:
    """Represents a response from the VLLM API."""

    def __init__(self, message: str, tool_call_id: str, tool_calls: list[dict]) -> None:
        """Initialize the VllmApiResponse object.

        Args:
            message (str): The response message.
            tool_call_id (str): The tool call ID.
            tool_calls (list[dict]): The list of tool calls.

        """
        self.message = message
        self.tool_call_id = tool_call_id
        self.tool_calls = tool_calls


class VllmModelsApiResponse:
    """Represents a response from the VLLM API."""

    def __init__(self, models: list[VllmModel]) -> None:
        """Initialize the VllmApiResponse object.

        Args:
            models (list[dict]): The list of models.

        """
        self.models = models


class VllmApiResponseDecoder:
    """Decode a VLLM API response."""

    @staticmethod
    def decode(response: dict) -> VllmChatApiResponse | VllmModelsApiResponse:
        """Decode a VLLM API response.

        Args:
            response (dict): The API response to decode.

        Returns:
            VllmChatApiResponse | VllmModelsApiResponse: The decoded API response.

        """
        if VllmApiResponseDecoder._contains_model_object(response):
            models = [
                VllmModel(model_id=model["id"]) for model in response["models"]
            ]
            return VllmModelsApiResponse(models=models)
        elif VllmApiResponseDecoder._contains_chat_completion_object(response):
            return VllmChatApiResponse(
                message=response["choices"][0]["message"]["content"],
                tool_call_id=response["choices"][0]["message"]["tool_call_id"],
                tool_calls=response["choices"][0]["message"]["tool_calls"],
            )
        else:
            raise ValueError("Unknown response object")

    @staticmethod
    def _contains_model_object(response: dict) -> bool:
        """Check if the response contains a model object.

        Args:
            response (dict): The API response to check.

        Returns:
            bool: True if the response contains a model object, False otherwise.

        """
        if isinstance(response, dict):
            if response.get("object") == "model":
                return True
            for _key, value in response.items():
                if VllmApiResponseDecoder._contains_model_object(value):
                    return True
        elif isinstance(response, list):
            for item in response:
                if VllmApiResponseDecoder._contains_model_object(item):
                    return True
        return False

    @staticmethod
    def _contains_chat_completion_object(response: dict) -> bool:
        """Check if the response contains a chat completion object.

        Args:
            response (dict): The API response to check.

        Returns:
            bool: True if the response contains a chat completion object, False otherwise.

        """
        if isinstance(response, dict):
            if response.get("object") == "chat.completion":
                return True
            for _key, value in response.items():
                if VllmApiResponseDecoder._contains_chat_completion_object(value):
                    return True
        elif isinstance(response, list):
            for item in response:
                if VllmApiResponseDecoder._contains_chat_completion_object(item):
                    return True
        return False
