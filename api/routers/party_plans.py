from fastapi import APIRouter, Body, HTTPException, status, Response, Depends
from datetime import datetime
from typing import List
from datetime import datetime
from uuid import UUID, uuid4
from bson.binary import Binary
from datetime import datetime, timedelta
from utils.authenticator import authenticator
from models.party_plans import (
    ApiMapsLocation,
    PartyPlan,
    PartyPlanUpdate,
    PartyPlanCreate,
)
from clients.client import db
from maps_api import geo_code
from fastapi.encoders import jsonable_encoder

router = APIRouter()


@router.post(
    "/",
    response_description="Create a new party plan",
    status_code=status.HTTP_201_CREATED,
    response_model=PartyPlan,
)
def create_party_plan(
    party_plan: PartyPlanCreate = Body(...),
):
    party_plan_data = jsonable_encoder(party_plan)
    party_plan_data["id"] = str(uuid4())
    party_plan_data["created"] = datetime.now()
    party_plan_data["party_status"] = "draft"

    address = party_plan_data["api_maps_location"][0]["input"]
    if address:
        geo_data = geo_code(address)
        if geo_data:
            party_plan_data["api_maps_location"][0]["geo"] = geo_data

    new_party_plan = db.party_plans.insert_one(party_plan_data)
    if not new_party_plan.acknowledged:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to add party plan to database.",
        )

    created_party_plan = db.party_plans.find_one({"id": party_plan_data["id"]})
    if not created_party_plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Party plan with ID {party_plan_data['id']} not found after insertion.",
        )

    return created_party_plan


@router.get(
    "/",
    response_description="List all party plans",
    response_model=List[PartyPlan],
)
def list_party_plans():
    party_plans = list(db.party_plans.find(limit=100))
    for party in party_plans:
        invitations = list(db.invitations.find({"party_plan_id": party["id"]}))
        party["invitations"] = [inv["id"] for inv in invitations]

    return party_plans


@router.get(
    "/{id}",
    response_description="Get a single party plan by ID",
    response_model=PartyPlan,
)
def find_party_plan(
    id: str,
):
    party_plan = db.party_plans.find_one({"id": id})
    if party_plan:
        invitations = list(
            db.invitations.find({"party_plan_id": party_plan["id"]})
        )
        party_plan["invitations"] = [inv["id"] for inv in invitations]

        return party_plan
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Party plan with ID {id} not found",
    )


@router.put(
    "/{id}",
    response_description="Update a party plan",
    response_model=PartyPlan,
)
def update_party_plan(
    id: UUID,
    party_plan: PartyPlanUpdate = Body(...),
):
    existing_party_plan = db.party_plans.find_one({"id": str(id)})
    if not existing_party_plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Party with ID {id} not found",
        )

    party_plan_data = {
        k: v for k, v in party_plan.dict().items() if v is not None
    }

    if "searched_locations" in party_plan_data:
        existing_searched_locations = existing_party_plan.get(
            "searched_locations", []
        )

        existing_place_ids = {
            location["place_id"] for location in existing_searched_locations
        }

        for location_place_id in party_plan_data["searched_locations"]:
            place_id = location_place_id["place_id"]
            if place_id not in existing_place_ids:
                if place_id not in existing_place_ids:
                    location = db.locations.find_one(
                        {"place_id": str(place_id)}
                    )

                    if not location:
                        raise HTTPException(
                            status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Location with ID {location} not found.",
                        )

                    notes = party_plan_data.get("notes")
                    account_location_tags = location.get(
                        "account_location_tags"
                    )
                    location_data = {
                        "place_id": place_id,
                        "account_location_tags": account_location_tags,
                        "notes": notes,
                    }

                    existing_searched_locations.append(location_data)

        party_plan_data["searched_locations"] = existing_searched_locations

    if "favorite_locations" in party_plan_data:
        existing_searched_locations = existing_party_plan.get(
            "searched_locations", []
        )
        existing_favorite_locations = existing_party_plan.get(
            "favorite_locations", []
        )
        favorite_place_ids = [
            str(location.get("place_id"))
            for location in party_plan_data["favorite_locations"]
        ]
        if party_plan_data["favorite_locations"] is None:
            party_plan_data["favorite_locations"] = []
        existing_searched_location_ids = [
            str(location.get("place_id"))
            for location in existing_searched_locations
        ]
        existing_favorite_location_ids = [
            str(location.get("place_id"))
            for location in existing_favorite_locations
        ]
        if not all(
            place_id in existing_searched_location_ids
            for place_id in favorite_place_ids
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="All favorite locations must be part of searched locations.",
            )
        notes = party_plan_data.get("notes")
        account_location_tags = party_plan_data.get("account_location_tags")

        for fav_location in party_plan_data["favorite_locations"]:
            if (
                str(fav_location.get("place_id"))
                in existing_favorite_location_ids
            ):
                fav_location["notes"] = fav_location.get("notes")
                fav_location["account_location_tags"] = fav_location.get(
                    "account_location_tags"
                )
            if not isinstance(fav_location, dict):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Each item in favorite_locations must be a dictionary.",
                )

            location_data = {
                "place_id": str(fav_location.get("place_id")),
                "account_location_tags": fav_location.get(
                    "account_location_tags"
                ),
                "notes": fav_location.get("notes"),
            }
            existing_favorite_locations.append(location_data)

    if "chosen_locations" in party_plan_data:
        existing_favorite_locations = existing_party_plan.get(
            "favorite_locations", []
        )
        if not all(
            chosen_id in existing_favorite_locations
            for chosen_id in party_plan_data["chosen_locations"]
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="All chosen locations must be part of favorite locations.",
            )
        party_plan_data["chosen_locations"] = [
            chosen_id for chosen_id in party_plan_data["chosen_locations"]
        ]

    if "invitations" in party_plan_data:
        invitations_to_validate = party_plan_data["invitations"]
        associated_invitations = list(
            db.invitations.find({"party_plan_id": str(id)})
        )
        associated_invitation_ids = {
            str(invitation["id"]) for invitation in associated_invitations
        }
        if not all(
            str(invitation_id) in associated_invitation_ids
            for invitation_id in invitations_to_validate
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Some provided invitation IDs are not associated with this party plan.",
            )

        party_plan_data["invitations"] = [
            UUID(str(inv_id)) for inv_id in invitations_to_validate
        ]

    current_time = datetime.now()
    party_plan_data["updated"] = current_time

    db.party_plans.update_one({"id": str(id)}, {"$set": party_plan_data})

    return db.party_plans.find_one({"id": str(id)})

@router.put(
    "/{id}/final/",
    response_description="finalize a party plan",
    response_model=PartyPlan,
)
def finalize_party_plan(
    id: UUID,
    party_plan: PartyPlanUpdate = Body(...),
    # account: dict = Depends(authenticator.get_current_account_data),
):
    existing_party_plan = db.party_plans.find_one({"id": str(id)})
    if not existing_party_plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Party with ID {id} not found",
        )


@router.delete("/{id}", response_description="Delete a party plan")
def delete_party_plan(
    id: str,
    response: Response,
):
    delete_result = db.party_plans.delete_one({"id": id})
    if delete_result.deleted_count == 1:
        return {
            "status": "success",
            "message": f"Party plan with ID {id} successfully deleted.",
        }
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"No party plan with ID {id} found. Deletion incomplete.",
    )
