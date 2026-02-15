from enum import IntEnum
from pathlib import Path
import json
import os

from fastapi import Depends, FastAPI, Header, HTTPException, status
from pydantic import BaseModel, Field


class AttendanceOption(IntEnum):
    YES = 1
    NO = 2
    LATER = 3


class GuestResponseCreate(BaseModel):
    guests: list[str] = Field(min_length=1)
    attendance: AttendanceOption


class GuestResponse(BaseModel):
    guest: str
    attendance: AttendanceOption


ROOT_DIR = Path(__file__).resolve().parents[2]
DATA_FILE = ROOT_DIR / "guests.json"
API_KEY = os.getenv("WEDDING_API_KEY")

app = FastAPI(title="Wedding Backend")


def _check_authorization(
    authorization: str | None = Header(default=None, alias="Authorization"),
) -> None:
    if not API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Server auth key is not configured",
        )
    if authorization is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization key is required",
        )
    valid_values = {API_KEY, f"Bearer {API_KEY}"}
    if authorization not in valid_values:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization key",
        )


def _ensure_data_file() -> None:
    if not DATA_FILE.exists():
        DATA_FILE.write_text("[]", encoding="utf-8")


def _read_responses() -> list[dict]:
    _ensure_data_file()
    with DATA_FILE.open("r", encoding="utf-8") as data_file:
        data = json.load(data_file)
    normalized: list[dict] = []
    for item in data:
        if "guest" in item and "attendance" in item:
            normalized.append(
                {
                    "guest": item["guest"],
                    "attendance": int(item["attendance"]),
                }
            )
            continue
        if "guests" in item and "attendance" in item:
            for guest_name in item["guests"]:
                normalized.append(
                    {
                        "guest": guest_name,
                        "attendance": int(item["attendance"]),
                    }
                )
    return normalized


def _write_responses(responses: list[dict]) -> None:
    with DATA_FILE.open("w", encoding="utf-8") as data_file:
        json.dump(responses, data_file, ensure_ascii=False, indent=2)


@app.post("/guests", response_model=list[GuestResponse])
def create_guest_response(
    payload: GuestResponseCreate,
    _: None = Depends(_check_authorization),
) -> list[GuestResponse]:
    created_items = [
        {
            "guest": guest_name,
            "attendance": int(payload.attendance),
        }
        for guest_name in payload.guests
    ]
    responses = _read_responses()
    responses.extend(created_items)
    _write_responses(responses)
    return [GuestResponse.model_validate(item) for item in created_items]


@app.get("/guests", response_model=list[GuestResponse])
def list_guest_responses(_: None = Depends(_check_authorization)) -> list[GuestResponse]:
    responses = _read_responses()
    return [GuestResponse.model_validate(item) for item in responses]
