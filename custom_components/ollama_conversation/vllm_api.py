"""VLLM API Client for Ollama Conversation."""

from __future__ import annotations

import asyncio
import socket

import aiohttp
import async_timeout

from .exceptions import (
    ApiClientError,
    ApiCommError,
    ApiJsonError,
    ApiTimeoutError
)

from .response import VllmApiResponseDecoder, VllmChatApiResponse, VllmModelsApiResponse

from .const import LOGGER


class VllmApiClient:
    """API client for VLLM."""

    def __init__(
        self,
        base_url: str,
        timeout: int,
        session: aiohttp.ClientSession,
    ) -> None:
        """VLLM API Client."""
        self._base_url = base_url.rstrip("/")
        self.timeout = timeout
        self._session = session

    async def async_get_heartbeat(self) -> bool:
        """Get heartbeat from the API."""
        response = await self.async_get_models()
        return len(response.models) > 0

    async def async_get_models(self) -> VllmModelsApiResponse:
        """Get models from the API."""
        response = await self._api_wrapper(
            method="get", url=f"{self._base_url}/v1/models",
            headers={
                "Content-type": "application/json; charset=UTF-8",
                "Authorization": "Bearer functionary"
            },)
        decoded_response: VllmModelsApiResponse = VllmApiResponseDecoder.decode(
            response)
        return decoded_response

    async def async_chat(self, data: dict | None = None,) -> VllmChatApiResponse:
        """Chat with the API."""
        response = await self._api_wrapper(
            method="post",
            url=f"{self._base_url}/v1/chat/completions",
            data=data,
            headers={
                "Content-type": "application/json; charset=UTF-8",
                "Authorization": "Bearer functionary"
            },)
        LOGGER.debug("API response: %s", response)
        decoded_response: VllmChatApiResponse = VllmApiResponseDecoder.decode(
            response)

        return decoded_response

    async def _api_wrapper(
        self,
        method: str,
        url: str,
        data: dict | None = None,
        headers: dict | None = None,
        decode_json: bool = True,
    ) -> any:
        """Get information from the API."""
        try:
            async with async_timeout.timeout(self.timeout):
                response = await self._session.request(
                    method=method,
                    url=url,
                    headers=headers,
                    json=data,
                )

                if response.status == 404 and decode_json:
                    json = await response.json()
                    raise ApiJsonError(json["error"])

                response.raise_for_status()

                if decode_json:
                    return await response.json()
                return await response.text()
        except ApiJsonError as e:
            raise e
        except asyncio.TimeoutError as e:
            raise ApiTimeoutError("timeout while talking to the server") from e
        except (aiohttp.ClientError, socket.gaierror) as e:
            raise ApiCommError(
                "unknown error while talking to the server") from e
        except Exception as e:  # pylint: disable=broad-except
            raise ApiClientError("something really went wrong!") from e
