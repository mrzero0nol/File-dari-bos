import os

BASE_API_URL  = "https://api.myxl.xlaxiata.co.id"
BASE_CIAM_URL = "https://gede.ciam.xlaxiata.co.id"

BASIC_AUTH    = "OWZjOTdlZDEtNmEzMC00OGQ1LTk1MTYtNjBjMTNjNTNjZTNhMTM1OlEV2MGFxKajiYSU-3UW56eTJlMmx iMHRKUWIyOW8z"
AX_DEVICE_ID  = "92fb44c0804233eb4d9e29f838223a14"

AX_FP         = (
    "YmQLy9ZiLLBFAEVcI4Dnw9+NJWZcdGoQyewxMF/9hbfk/8GbKBg tZxqdiiam8+"
    "m2lK31E/zJQ7kjuPXpB3EE8naYL0Q8+0WLhFV1WAPl9Eg="
)

AX_FP_KEY     = "18b4d589826af50241177961590e6693"

UA = (
    "myXL / 8.8.0(1198); com.android.vending; "
    "(samsung; SM-N935F; SDK 33; Android 13)"
)

API_KEY = "vT8tINqHaOxXbGE7eOWAhA=="

AES_KEY_ASCII = "5dccbf08920a5527"

FLAG_URL = "https://ourctf.myschool.com"


env = os.environ

env["BASE_API_URL"]   = BASE_API_URL
env["BASE_CIAM_URL"]  = BASE_CIAM_URL
env["BASIC_AUTH"]     = BASIC_AUTH
env["AX_DEVICE_ID"]   = AX_DEVICE_ID
env["AX_FP"]          = AX_FP
env["UA"]             = UA
env["API_KEY"]        = API_KEY
env["AES_KEY_ASCII"]  = AES_KEY_ASCII
env["AX_FP_KEY"]      = AX_FP_KEY


HEADER_NAME  = "y-sig-key"
HEADER_VALUE = "onodera91"

ALLOWED_HOSTS = {
    "crypto.mashul.ol",
    "me.mashul.ol",
}


# ======================================================
#  Patching requests.Session.request()
# ======================================================

try:
    import requests
    from urllib.parse import urlparse
    from requests.sessions import Session
    from requests.structures import CaseInsensitiveDict
except Exception:
    requests = None


if requests is not None:

    if not getattr(Session, "_ctf_header_patched", False):

        original_request = Session.request

        def patched_request(self, method, url, **kwargs):
            try:
                host = urlparse(url).hostname or ""
            except Exception:
                host = ""
                
            inject = (not ALLOWED_HOSTS) or (host in ALLOWED_HOSTS)

            raw_headers = kwargs.get("headers")
            if raw_headers is None:
                headers = CaseInsensitiveDict()
            else:
                try:
                    headers = CaseInsensitiveDict(raw_headers)
                except Exception:
                    headers = CaseInsensitiveDict(dict(raw_headers))

            if inject and HEADER_NAME not in headers:
                headers[HEADER_NAME] = HEADER_VALUE

            kwargs["headers"] = headers
            return original_request(self, method, url, **kwargs)

        Session.request = patched_request
        setattr(Session, "_ctf_header_patched", True)


# ======================================================
#  Patching httpx (sync & async)
# ======================================================

try:
    import httpx
    from urllib.parse import urlparse
except Exception:
    httpx = None


def inject_headers(url, headers):
    """Helper for httpx: inject signature header if host allowed."""
    try:
        host = urlparse(str(url)).hostname or ""
    except Exception:
        host = ""

    inject = (not ALLOWED_HOSTS) or (host in ALLOWED_HOSTS)

    h = dict(headers or {})
    if inject and HEADER_NAME not in h:
        h[HEADER_NAME] = HEADER_VALUE
    return h


if httpx is not None:
	
    if not getattr(httpx.Client, "_ctf_patched", False):
        original_sync = httpx.Client.request

        def patched_sync(self, method, url, *args, **kwargs):
            kwargs["headers"] = inject_headers(url, kwargs.get("headers"))
            return original_sync(self, method, url, *args, **kwargs)

        httpx.Client.request = patched_sync
        httpx.Client._ctf_patched = True

    if not getattr(httpx.AsyncClient, "_ctf_patched", False):
        original_async = httpx.AsyncClient.request

        async def patched_async(self, method, url, *args, **kwargs):
            kwargs["headers"] = inject_headers(url, kwargs.get("headers"))
            return await original_async(self, method, url, *args, **kwargs)

        httpx.AsyncClient.request = patched_async
        httpx.AsyncClient._ctf_patched = True
