from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, Dict, List
from datetime import date, datetime
from uuid import UUID
from enum import Enum


class PartyStatus(str, Enum):
    DRAFT = "draft"
    SHARE_DRAFT = "share draft"
    FINALIZED = "finalized"


class GeoJSON(BaseModel):
    type: str = "Point"
    coordinates: List[float] = Field(..., min_items=2, max_items=2)
    expires: Optional[datetime]


class ApiMapsLocation(BaseModel):
    geo: Optional[GeoJSON]
    input: Optional[str]


class PartyPlan(BaseModel):
    id: UUID
    # account_id: Optional[str]
    created: datetime
    updated: Optional[datetime]
    api_maps_location: List[ApiMapsLocation]
    start_time: Optional[datetime]
    endpoint: Optional[str]
    end_time: Optional[datetime]
    description: Optional[str]
    image: Optional[HttpUrl]
    party_status: Optional[PartyStatus]
    invitations: Optional[List[UUID]]
    keywords: Optional[List[str]]
    searched_locations: Optional[List[UUID]]
    favorite_locations: Optional[List[UUID]]
    chosen_locations: Optional[List[UUID]]

    class Config:
        allow_population_by_field_name = True
        schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "account_id": "123456789",
                "created": "2022-02-22T14:30:00",
                "updated": "2022-02-22T16:30:00",
                "api_maps_location": [
                    {
                        "geo": {
                            "type": "Point",
                            "coordinates": [40.7128, -74.0060],
                            "expires": "2023-09-24T22:42:00.402000",
                        },
                        "input": "New York, NY",
                    }
                ],
                "start_time": "2022-02-22T14:30:00",
                "end_time": "2022-02-22T17:30:00",
                "description": "Description here ....",
                "image": "https://picsum.photos/200",
                "party_status": "draft",
                "invitations": ["id1", "id2"],
                "keywords": ["fun", "bar", "burgers"],
                "searched_locations": [
                    "location_id1",
                    "location_id2",
                    "location_id3",
                ],
                "favorite_locations": ["location_id1", "location_id2"],
                "chosen_locations": ["location_id2"],
            }
        }


class PartyPlanCreate(BaseModel):
    # id, account_id, created, party_status auto-generated
    # account_id: str
    api_maps_location: List[ApiMapsLocation]
    start_time: datetime
    endpoint: Optional[str]
    end_time: Optional[datetime]
    description: Optional[str]
    image: Optional[HttpUrl]
    keywords: Optional[List[str]]

    class Config:
        schema_extra = {
            "example": {
                "account_id": "123456789",
                "api_maps_location": [
                    {
                        "input": "New York, NY",
                    }
                ],
                "start_time": "2022-02-23T14:30:00",
                "end_time": "2022-02-23T17:30:00",
                "description": "Updated Description here ....",
                "image": "https://picsum.photos/201",
                "keywords": ["party", "drinks", "dance"],
            }
        }


class PartyPlanUpdate(BaseModel):
    api_maps_location: Optional[List[ApiMapsLocation]]
    start_time: Optional[datetime]
    end_time: Optional[datetime]
    description: Optional[str]
    image: Optional[HttpUrl]
    invitations: Optional[List[UUID]]
    party_status: Optional[PartyStatus]
    keywords: Optional[List[str]]
    searched_locations: Optional[List[UUID]]
    favorite_locations: Optional[List[UUID]]
    chosen_locations: Optional[List[UUID]]

    class Config:
        schema_extra = {
            "example": {
                "api_maps_location": [
                    {
                        "geo": {
                            "type": "Point",
                            "coordinates": [40.7128, -74.0060],
                        },
                        "input": "New York, NY",
                    }
                ],
                "start_time": "2022-02-23T14:30:00",
                "end_time": "2022-02-23T17:30:00",
                "description": "Updated Description here ....",
                "image": "https://picsum.photos/201",
                "party_status": "share draft",
                "invitations": ["<INSERT VALID INVITATION"],
                "keywords": ["party", "drinks", "dance"],
                "searched_locations": [
                    "<placeid1 REPLACE ME>",
                    "<placeid2 REPLACE ME>",
                ],
                "favorite_locations": [
                    "<placeid1 REPLACE ME>",
                    "<placeid2 REPLACE ME>",
                ],
                "chosen_locations": ["<placeid2 REPLACE ME>"],
            }
        }
