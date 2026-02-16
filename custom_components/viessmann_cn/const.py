"""Constants for Viessmann API."""

API_BASE_URL = "https://api.viessmann.cn"

# Endpoints
ENDPOINT_LOGIN = "/idass/user/login"
ENDPOINT_USER_INFO = "/idass/user/info"
ENDPOINT_FAMILY_LIST = "/api/family/list"
ENDPOINT_FAMILY_DEVICES = "/api/home/familyDevices/v2"
ENDPOINT_DEVICE_DETAIL = "/api/device/detail"
ENDPOINT_SCAN_STATUS = "/api/device/scanStatus"

# Control Endpoints
ENDPOINT_SET_CH_TEMP = "/api/3/sendToDevice/setChsetTemp"
ENDPOINT_SET_DHW_TEMP = "/api/3/sendToDevice/setDhwTemp"
ENDPOINT_SET_MODE = "/api/3/sendToDevice/setMode"

# Headers
DEFAULT_HEADERS = {
    "User-Agent": "FeiSiMan/5.0.5 (iPhone; iOS 26.2.1; Scale/3.00)",
    "Accept-Language": "zh-Hans;q=1",
    "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8",
    "innerKey": "81F862CB8ABBE1FD66E7C452431CE679",
}
