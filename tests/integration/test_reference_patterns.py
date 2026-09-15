import json
from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)

EXPECTED_PATTERNS = {
    "clustered_1": "Patrón agrupado",
    "regular_1": "Patrón regular",
    "line_1": "Patrón Line",
    "diagonal_1": "Patrón Diag",
}

PATTERNS_FILE = (
    Path(__file__).resolve().parents[2]
    / "test_data"
    / "patterns"
    / "reference_patterns.json"
)


def load_cases():
    with PATTERNS_FILE.open("r", encoding="utf-8") as file:
        return json.load(file)


def test_reference_patterns_are_analyzable():
    data = load_cases()

    for case in data["cases"]:
        response = client.post(
            "/api/v1/analysis",
            json={
                "image_width": data["image_width"],
                "image_height": data["image_height"],
                "alpha": data["alpha"],
                "points": case["points"],
            },
        )

        assert response.status_code == 200, (
            f"El caso '{case['name']}' no pudo analizarse: "
            f"{response.text}"
        )

        result = response.json()
        security = result["security"]

        assert security["is_weak"] == case["expected_weak"]

        expected_pattern = case.get(
            "expected_pattern",
            EXPECTED_PATTERNS.get(case["name"]),
        )

        if expected_pattern is not None:
            assert expected_pattern in security["patterns"], (
                f"El caso '{case['name']}' debía incluir el patrón "
                f"'{expected_pattern}', pero recibió "
                f"{security['patterns']}"
            )

        print(f"\n{'=' * 50}")
        print(f"CASO: {case['name']}")
        print(f"DESCRIPCIÓN: {case['description']}")
        print(f"IS_WEAK: {security['is_weak']}")
        print(f"NIVEL: {security['level']}")
        print(f"PATRONES: {security['patterns']}")
        print(f"TÍTULO: {security['title']}")
        print(f"EXPLICACIÓN: {security['explanation']}")
        print(
            f"PERÍMETROS: "
            f"{result['perimeter_test']['reject_null']}"
        )
        print(
            f"ÁNGULOS: "
            f"{result['angle_test']['reject_null']}"
        )