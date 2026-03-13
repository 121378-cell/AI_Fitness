import time
from typing import Any, Dict, Optional

import requests


class HttpRequestError(RuntimeError):
    pass


def request_json(
    method: str,
    url: str,
    *,
    headers: Optional[Dict[str, str]] = None,
    params: Optional[Dict[str, Any]] = None,
    json: Optional[Dict[str, Any]] = None,
    timeout_s: int = 20,
    retries: int = 3,
    backoff_s: float = 1.0,
) -> Dict[str, Any]:
    """HTTP JSON helper with timeout + retry + exponential backoff."""
    last_error: Optional[Exception] = None

    for attempt in range(1, retries + 1):
        try:
            response = requests.request(
                method=method,
                url=url,
                headers=headers,
                params=params,
                json=json,
                timeout=timeout_s,
            )
            if response.status_code >= 500:
                raise HttpRequestError(f"Server error {response.status_code}: {response.text[:300]}")
            if response.status_code >= 400:
                raise HttpRequestError(f"HTTP {response.status_code}: {response.text[:300]}")
            return response.json()
        except (requests.RequestException, ValueError, HttpRequestError) as exc:
            last_error = exc
            if attempt == retries:
                break
            time.sleep(backoff_s * (2 ** (attempt - 1)))

    raise HttpRequestError(f"Request failed after {retries} attempts: {last_error}")
