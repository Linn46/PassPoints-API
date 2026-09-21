from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from app.domain.point import Point
from app.application.analysis.service import AnalysisService

PATTERNS_FILE = (
    ROOT
    / "test_data"
    / "patterns"
    / "reference_patterns.json"
)


def load_data() -> dict:
    with PATTERNS_FILE.open("r", encoding="utf-8") as file:
        return json.load(file)


def main() -> int:
    data = load_data()
    service = AnalysisService()

    failures = []

    print("=" * 60)
    print("PASSPOINTS API - AUDITORÍA DE PATRONES")
    print("=" * 60)

    for case in data["cases"]:
        points = [
            Point(**point)
            for point in case["points"]
        ]

        result = service.analyze(
            points,
            data["image_width"],
            data["image_height"],
            data["alpha"],
        )

        security = result.security
        expected_weak = case["expected_weak"]
        expected_pattern = case.get("expected_pattern")

        weak_ok = security.is_weak == expected_weak

        pattern_ok = (
            expected_pattern is None
            or expected_pattern in security.patterns
        )

        ok = weak_ok and pattern_ok

        status = "OK" if ok else "FAIL"

        print(
            f"[{status}] {case['name']} | "
            f"esperado={expected_pattern or 'ninguno'} | "
            f"obtenido={security.patterns or 'ninguno'}"
        )

        if not ok:
            failures.append(case["name"])

    print("\n" + "=" * 60)

    if failures:
        print(f"FALLAS: {len(failures)}")
        for failure in failures:
            print(f" - {failure}")
        return 1

    print(f"RESULTADO: {len(data['cases'])}/{len(data['cases'])} casos correctos")
    print("ESTADO: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())