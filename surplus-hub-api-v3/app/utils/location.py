import json
from typing import Optional


class LocationData:
    """위치 데이터 검증 및 직렬화"""

    def __init__(
        self,
        latitude: float,
        longitude: float,
        address: Optional[str] = None,
        title: Optional[str] = None,
    ):
        if not (-90 <= latitude <= 90):
            raise ValueError("latitude must be between -90 and 90")
        if not (-180 <= longitude <= 180):
            raise ValueError("longitude must be between -180 and 180")
        self.latitude = latitude
        self.longitude = longitude
        self.address = address
        self.title = title

    def to_json_string(self) -> str:
        data: dict = {"latitude": self.latitude, "longitude": self.longitude}
        if self.address:
            data["address"] = self.address
        if self.title:
            data["title"] = self.title
        return json.dumps(data, ensure_ascii=False)

    @classmethod
    def from_dict(cls, data: dict) -> "LocationData":
        if not isinstance(data, dict):
            raise ValueError("location data must be a dictionary")
        lat = data.get("latitude")
        lng = data.get("longitude")
        if lat is None or lng is None:
            raise ValueError("latitude and longitude are required")
        return cls(
            latitude=float(lat),
            longitude=float(lng),
            address=data.get("address"),
            title=data.get("title"),
        )

    @classmethod
    def from_json_string(cls, s: str) -> "LocationData":
        return cls.from_dict(json.loads(s))
