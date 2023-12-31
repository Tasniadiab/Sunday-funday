from datetime import datetime
from enum import Enum
from typing import Dict, Optional
from uuid import UUID
from pydantic import BaseModel


class SentStatus(str, Enum):
    PENDING = "pending"
    SENT = "sent"
    DELIVERED = "delivered"
    FAILED = "failed"
    OPENED = "opened"


class EmailContext(BaseModel):
    invitation_id: UUID
    created_at: datetime
    updated_at: Optional[datetime]
    account: Dict[str, str]
    party_plan_id: UUID
    sent_status: SentStatus


class ApiEmail(BaseModel):
    id: UUID
    to: str
    subject: str
    template: str
    api_context: EmailContext

    class Config:
        allow_population_by_field_name = True
        schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "to": "John Doe <john.doe@example.com>",
                "subject": "Your Invitation",
                "template": "invitation_template",
                "api_context": {
                    "invitation_id": "123e4567-e89b-12d3-a456-426614174001",
                    "created_at": "2023-08-28T14:12:12Z",
                    "updated_at": "2023-08-28T16:12:12Z",
                    "account": {
                        "id": "123e4567-e89b-12d3-a456-426614174001",
                        "fullname": "John Doe",
                        "email": "john.doe@example.com",
                    },
                    "party_plan_id": "123e4567-e89b-12d3-a456-426614174002",
                    "rsvp_status": "yes",
                    "sent_status": "sent",
                },
            }
        }
