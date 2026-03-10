import csv
import io
from pathlib import Path
import json

from fastapi.testclient import TestClient

from wedding_backend import main


def _make_client(tmp_path: Path) -> TestClient:
    main.DATA_FILE = tmp_path / "guests.json"
    main.API_KEY = "test-key"
    return TestClient(main.app)


def test_create_guest_response_stores_phone_per_guest(tmp_path: Path) -> None:
    client = _make_client(tmp_path)

    response = client.post(
        "/guests",
        headers={"Authorization": "test-key"},
        json={
            "guests": ["Alice", "Bob"],
            "phone": "+79990001122",
            "attendance": 1,
        },
    )

    assert response.status_code == 200
    assert response.json() == [
        {"guest": "Alice", "phone": "+79990001122", "attendance": 1},
        {"guest": "Bob", "phone": "+79990001122", "attendance": 1},
    ]

    with main.DATA_FILE.open("r", encoding="utf-8") as data_file:
        stored = json.load(data_file)

    assert stored == [
        {"guest": "Alice", "phone": "+79990001122", "attendance": 1},
        {"guest": "Bob", "phone": "+79990001122", "attendance": 1},
    ]


def test_list_guest_responses_reads_phone_from_legacy_grouped_records(tmp_path: Path) -> None:
    client = _make_client(tmp_path)

    grouped_records = [
        {"guests": ["Alice", "Bob"], "phone": "+79990001122", "attendance": 1},
        {"guests": ["Charlie"], "attendance": 2},
    ]
    main.DATA_FILE.write_text(
        json.dumps(grouped_records, ensure_ascii=False),
        encoding="utf-8",
    )

    response = client.get(
        "/guests",
        headers={"Authorization": "Bearer test-key"},
    )

    assert response.status_code == 200
    assert response.json() == [
        {"guest": "Alice", "phone": "+79990001122", "attendance": 1},
        {"guest": "Bob", "phone": "+79990001122", "attendance": 1},
        {"guest": "Charlie", "phone": None, "attendance": 2},
    ]


def test_export_guest_responses_csv_includes_phone_column(tmp_path: Path) -> None:
    client = _make_client(tmp_path)

    rows = [
        {"guest": "Alice", "phone": "+79990001122", "attendance": 1},
        {"guest": "Bob", "phone": None, "attendance": 3},
    ]
    main.DATA_FILE.write_text(
        json.dumps(rows, ensure_ascii=False),
        encoding="utf-8",
    )

    response = client.get(
        "/guests/csv",
        headers={"Authorization": "test-key"},
    )

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/csv")
    assert response.text.startswith("\ufeff")
    csv_payload = response.text.removeprefix("\ufeff")
    parsed_rows = list(csv.DictReader(io.StringIO(csv_payload)))

    assert parsed_rows == [
        {
            "guest": "Alice",
            "phone": "+79990001122",
            "attendance": "1",
            "attendance_label": "Да, с удовольствием",
        },
        {
            "guest": "Bob",
            "phone": "",
            "attendance": "3",
            "attendance_label": "Отвечу позже (до 25.04.2026)",
        },
    ]
