import aiohttp
import logging
from typing import Dict, List, Optional, Any

from .const import (
    API_BASE_URL,
    ENDPOINT_LOGIN,
    ENDPOINT_USER_INFO,
    ENDPOINT_FAMILY_LIST,
    ENDPOINT_FAMILY_DEVICES,
    ENDPOINT_DEVICE_DETAIL,
    ENDPOINT_SCAN_STATUS,
    ENDPOINT_SET_CH_TEMP,
    ENDPOINT_SET_DHW_TEMP,
    ENDPOINT_SET_MODE,
    DEFAULT_HEADERS,
)
from .exceptions import AuthError, NetworkError, ApiError

_LOGGER = logging.getLogger(__name__)


class ViessmannClient:
    """Async client for Viessmann API."""

    def __init__(
        self,
        username: str,
        password: str,
        session: Optional[aiohttp.ClientSession] = None,
    ):
        self._username = username
        self._password = password
        self._session = session
        self._token: Optional[str] = None
        self._user_id: Optional[str] = None
        self._family_id: Optional[str] = None
        self._physics_id: Optional[str] = None
        self._device_info: Dict[str, Any] = {}

    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create aiohttp session."""
        if self._session is None:
            self._session = aiohttp.ClientSession()
        return self._session

    async def _request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict] = None,
        json_data: Optional[Dict] = None,
        headers: Optional[Dict] = None,
        params: Optional[Dict] = None,
        retry_auth: bool = True,
    ) -> Dict:
        """Make an API request."""
        session = await self._get_session()
        url = f"{API_BASE_URL}{endpoint}"

        # Prepare headers and params
        # We copy them to avoid modifying the caller's objects and to allow updates on retry
        req_headers = DEFAULT_HEADERS.copy()
        if headers:
            req_headers.update(headers)

        req_params = params.copy() if params else {}

        # Inject token if available
        if self._token:
            req_headers["Authorization"] = self._token

            # Special handling for endpoints that require token in specific fields
            # Update authToken if it exists in headers or params
            if "authToken" in req_headers:
                req_headers["authToken"] = self._token
            if "authToken" in req_params:
                req_params["authToken"] = self._token

        try:
            async with session.request(
                method,
                url,
                data=data,
                json=json_data,
                headers=req_headers,
                params=req_params or None,
            ) as response:
                if response.status == 401:
                    if retry_auth and endpoint != ENDPOINT_LOGIN:
                        _LOGGER.info("Token expired, logging in again...")
                        await self.login()
                        # Retry the request with the new token
                        # The recursive call will pick up the new self._token and update headers/params
                        return await self._request(
                            method,
                            endpoint,
                            data,
                            json_data,
                            headers,  # Pass original headers
                            params,  # Pass original params
                            retry_auth=False,
                        )
                    raise AuthError("Unauthorized")

                try:
                    resp_json = await response.json()
                except Exception:
                    text = await response.text()
                    _LOGGER.error(f"Failed to parse JSON response from {url}: {text}")
                    raise ApiError(f"Invalid JSON response from {url}")

                if resp_json.get("code") != 0:
                    msg = resp_json.get("msg", "Unknown error")
                    _LOGGER.error(f"API Error {resp_json.get('code')}: {msg}")
                    raise ApiError(f"API Error: {msg}")

                return resp_json

        except aiohttp.ClientError as e:
            raise NetworkError(f"Network error: {e}")

    async def login(self) -> None:
        """Login to get access token."""
        # Clear existing token before login to avoid sending invalid token in headers
        self._token = None

        payload = {"phone": self._username, "password": self._password}

        # Login endpoint uses JSON
        headers = {"Content-Type": "application/json"}

        try:
            # Try to use json_data parameter which aiohttp supports
            resp = await self._request(
                "POST", ENDPOINT_LOGIN, json_data=payload, headers=headers
            )

            # Check if response structure matches expectation
            # HAR shows: {"msg": "操作成功", "code": 0, "data": {"statusCode": 200, "data": {"access_token": ...}}}
            data = resp.get("data", {}).get("data", {})
            self._token = data.get("access_token")

            if not self._token:
                # Fallback: maybe structure is different or token is in top level data?
                # Let's print response for debugging if token is missing
                _LOGGER.warning(f"Login response structure unexpected: {resp}")
                raise AuthError("Login successful but no token received")

        except ApiError as e:
            # If API returns 500, it might be due to wrong password or format
            # HAR shows 500 for wrong password
            if "500" in str(e):
                raise AuthError("Login failed: Invalid credentials or server error")
            raise AuthError(f"Login failed: {e}")

    async def get_user_info(self) -> Dict:
        """Get user info to retrieve user_id."""
        if not self._token:
            await self.login()

        # Based on HAR, this endpoint uses authToken query param AND header
        # And it also has innerKey
        params = {"authToken": self._token}
        # HAR shows authToken in header too
        headers = {"authToken": self._token}

        resp = await self._request(
            "GET", ENDPOINT_USER_INFO, headers=headers, params=params
        )

        data = resp.get("data", {})
        self._user_id = str(data.get("userId"))
        return data

    async def get_family_list(self) -> List[Dict]:
        """Get family list to retrieve family_id."""
        if not self._user_id:
            await self.get_user_info()

        payload = {"userId": self._user_id}
        resp = await self._request("POST", ENDPOINT_FAMILY_LIST, data=payload)

        families = resp.get("data", [])
        if families:
            # Default to first family
            self._family_id = str(families[0].get("familyId"))

        return families

    async def get_family_devices(self) -> Dict:
        """Get devices in the family."""
        if not self._family_id:
            await self.get_family_list()

        payload = {"familyId": self._family_id}
        resp = await self._request("POST", ENDPOINT_FAMILY_DEVICES, data=payload)

        data = resp.get("data", {}).get("defaultRoom", {})
        boilers = data.get("boilerInfos", [])

        if boilers:
            # Default to first boiler
            boiler = boilers[0]
            self._physics_id = str(boiler.get("physicsId"))
            self._device_info = boiler

        return data

    async def get_device_detail(self) -> Dict:
        """Get detailed status of the device."""
        if not self._physics_id:
            await self.get_family_devices()

        payload = {"physicsId": self._physics_id}
        resp = await self._request("POST", ENDPOINT_DEVICE_DETAIL, data=payload)

        # The response is a list, usually one item
        data = resp.get("data", [])
        if data:
            return data[0]
        return {}

    async def get_scan_status(self) -> Dict:
        """Get scan status of the device."""
        if not self._physics_id:
            await self.get_family_devices()

        payload = {"physicsId": self._physics_id}
        resp = await self._request("POST", ENDPOINT_SCAN_STATUS, data=payload)

        # The response is a list, usually one item
        data = resp.get("data", [])
        if data:
            return data[0]
        return {}

    async def set_heating_temp(self, temp: float) -> None:
        """Set central heating temperature."""
        if not self._physics_id:
            await self.get_family_devices()

        # API expects integer string for temperature
        payload = {"physicsIds": self._physics_id, "temp": str(int(temp))}
        await self._request("POST", ENDPOINT_SET_CH_TEMP, data=payload)

    async def set_dhw_temp(self, temp: float) -> None:
        """Set domestic hot water temperature."""
        if not self._physics_id:
            await self.get_family_devices()

        # API expects integer string for temperature
        payload = {"physicsIds": self._physics_id, "temp": str(int(temp))}
        await self._request("POST", ENDPOINT_SET_DHW_TEMP, data=payload)

    async def set_mode(self, mode: int) -> None:
        """Set device mode."""
        if not self._physics_id:
            await self.get_family_devices()

        payload = {"physicsIds": self._physics_id, "mode": str(mode)}
        await self._request("POST", ENDPOINT_SET_MODE, data=payload)

    async def update(self) -> Dict:
        """Update all data and return current status."""
        # Ensure we have IDs
        if not self._physics_id:
            await self.get_family_devices()

        # Get detail
        detail = await self.get_device_detail()

        return detail

    async def close(self):
        """Close the session."""
        if self._session:
            await self._session.close()
