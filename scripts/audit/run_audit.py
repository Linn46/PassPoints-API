import json
import subprocess
import sys
from pathlib import Path

from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from app.main import app


REFERENCE_FILE = ROOT / "test_data" / "patterns" / "reference_patterns.json"
SYNTHETIC_FILE = ROOT / "test_data" / "patterns" / "audit_cases.json"

client = TestClient(app)


def load_cases(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def expected_patterns(case: dict) -> list[str]:
    if "expected_patterns" in case:
        return case["expected_patterns"]

    return {
        "clustered_1": ["Patrón agrupado"],
        "regular_1": ["Patrón regular"],
        "line_1": ["Patrón Line"],
        "diagonal_1": ["Patrón Diag"],
        "random_1": [],
    }[case["name"]]


def transformed_case(case: dict, name: str, transform) -> dict:
    return {
        **case,
        "name": name,
        "points": [
            {
                "x": transform(point["x"], point["y"])[0],
                "y": transform(point["x"], point["y"])[1],
            }
            for point in case["points"]
        ],
    }


def build_cases() -> tuple[dict, ...]:
    reference = load_cases(REFERENCE_FILE)
    synthetic = load_cases(SYNTHETIC_FILE)

    cases = [
        {
            **case,
            "expected_patterns": expected_patterns(case),
        }
        for case in reference["cases"]
    ]

    cases.extend(synthetic["cases"])

    regular = next(
        case
        for case in synthetic["cases"]
        if case["name"] == "synthetic_regular"
    )

    cases.extend(
        (
            transformed_case(
                regular,
                "translated_regular",
                lambda x, y: (x + 120, y + 80),
            ),
            transformed_case(
                regular,
                "scaled_regular",
                lambda x, y: (x * 0.65 + 300, y * 0.65 + 180),
            ),
            transformed_case(
                regular,
                "perturbed_regular",
                lambda x, y: (x, y),
            ),
        )
    )

    perturbations = [
        (0, 0),
        (4, -3),
        (-3, 3),
        (3, 2),
        (-2, -2),
    ]

    cases[-1]["points"] = [
        {
            "x": point["x"] + delta[0],
            "y": point["y"] + delta[1],
        }
        for point, delta in zip(
            cases[-1]["points"],
            perturbations,
        )
    ]

    return tuple(cases)


def audit_case(
    case: dict,
    image_width: int,
    image_height: int,
    alpha: float,
) -> bool:
    response = client.post(
        "/api/v1/analysis",
        json={
            "image_width": image_width,
            "image_height": image_height,
            "alpha": alpha,
            "points": case["points"],
        },
    )

    if response.status_code != 200:
        print(
            f"[FAIL] {case['name']}: "
            f"status={response.status_code}"
        )
        return False

    security = response.json()["security"]

    expected_weak = case["expected_weak"]
    expected = case["expected_patterns"]
    actual = security["patterns"]

    passed = (
        security["is_weak"] == expected_weak
        and set(actual) == set(expected)
    )

    marker = "OK" if passed else "FAIL"

    print(
        f"[{marker}] {case['name']}: "
        f"weak={security['is_weak']} "
        f"patterns={actual}"
    )

    if not passed:
        print(
            f"       expected weak={expected_weak} "
            f"patterns={expected}"
        )

    return passed


def audit_patterns() -> bool:
    data = load_cases(SYNTHETIC_FILE)

    print("\n[CHECK] Auditoría de patrones")

    results = [
        audit_case(
            case,
            data["image_width"],
            data["image_height"],
            data["alpha"],
        )
        for case in build_cases()
    ]

    passed = sum(results)

    print(
        f"Patrones: {passed}/{len(results)} casos correctos"
    )

    return passed == len(results)


def run_pytest(label: str, path: str) -> bool:
    print(f"\n[CHECK] {label}")

    result = subprocess.run(
        [sys.executable, "-m", "pytest", path, "-q"],
        cwd=ROOT,
    )

    if result.returncode == 0:
        print("[OK]")
        return True

    print("[FAIL]")
    return False


def main() -> int:
    print("=" * 60)
    print("PASSPOINTS API - AUDITORÍA GENERAL")
    print("=" * 60)

    checks = [
        audit_patterns(),
        run_pytest(
            "Tests unitarios",
            "tests/unit",
        ),
        run_pytest(
            "Tests de integración",
            "tests/integration",
        ),
        run_pytest(
            "Tests de rendimiento",
            "tests/performance",
        ),
        run_pytest(
            "Suite completa",
            "tests",
        ),
    ]

    passed = sum(checks)

    print("\n" + "=" * 60)
    print("RESUMEN")
    print("=" * 60)
    print(f"Checks correctos: {passed}/{len(checks)}")

    if passed == len(checks):
        print("ESTADO: OK")
        return 0

    print("ESTADO: FAIL")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())