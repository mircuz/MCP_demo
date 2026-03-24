"""External REST API tools — weather, third-party data, etc."""

from __future__ import annotations

import json
from datetime import datetime, timezone


def register(mcp, w):
    """Register external-API tools with the MCP server."""

    @mcp.tool()
    def fetch_weather(latitude: float = 45.4642, longitude: float = 9.1900) -> str:
        """Fetch current weather data from the Open-Meteo API for a given location.

        Returns temperature, wind speed, humidity, and conditions with a UTC
        timestamp. Defaults to Milan, Italy.

        Args:
            latitude:  Latitude of the location (default 45.4642 — Milan).
            longitude: Longitude of the location (default 9.1900 — Milan).
        """
        import urllib.request

        url = (
            f"https://api.open-meteo.com/v1/forecast?"
            f"latitude={latitude}&longitude={longitude}"
            f"&current=temperature_2m,relative_humidity_2m,"
            f"wind_speed_10m,weather_code"
            f"&timezone=auto"
        )

        with urllib.request.urlopen(url, timeout=10) as resp:
            data = json.loads(resp.read().decode())

        current = data.get("current", {})
        units = data.get("current_units", {})

        payload = {
            "latitude": data.get("latitude"),
            "longitude": data.get("longitude"),
            "timezone": data.get("timezone"),
            "fetched_at_utc": datetime.now(timezone.utc).isoformat(),
            "temperature": f"{current.get('temperature_2m')} {units.get('temperature_2m', '')}",
            "relative_humidity": f"{current.get('relative_humidity_2m')} {units.get('relative_humidity_2m', '')}",
            "wind_speed": f"{current.get('wind_speed_10m')} {units.get('wind_speed_10m', '')}",
            "weather_code": current.get("weather_code"),
            "observation_time": current.get("time"),
        }
        return json.dumps(payload, indent=2)
