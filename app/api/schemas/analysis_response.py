from pydantic import BaseModel, ConfigDict


class PointResponse(BaseModel):
    x: float
    y: float


class TriangleResponse(BaseModel):
    vertices: list[PointResponse]


class PerimeterTestResponse(BaseModel):
    statistic: float
    critical_value: float
    alpha: float
    reject_null: bool


class AngleTestResponse(BaseModel):
    average_max_angle: float
    statistic: float
    critical_value: float
    alpha: float
    reject_null: bool


class SecurityResponse(BaseModel):
    is_weak: bool
    level: str
    patterns: list[str]
    title: str
    explanation: str


class AnalysisResponse(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "points": [
                        {"x": 100, "y": 100},
                        {"x": 500, "y": 100},
                        {"x": 500, "y": 500},
                        {"x": 100, "y": 500},
                        {"x": 300, "y": 300},
                    ],
                    "triangles": [
                        {
                            "vertices": [
                                {"x": 500, "y": 500},
                                {"x": 300, "y": 300},
                                {"x": 500, "y": 100},
                            ]
                        }
                    ],
                    "average_perimeter": 965.6854,
                    "average_max_angle": 90.0,
                    "perimeter_test": {
                        "statistic": -2.4114,
                        "critical_value": 1.96,
                        "alpha": 0.05,
                        "reject_null": True,
                    },
                    "angle_test": {
                        "average_max_angle": 90.0,
                        "statistic": -1.2674,
                        "critical_value": 1.6449,
                        "alpha": 0.05,
                        "reject_null": False,
                    },
                    "security": {
                        "is_weak": True,
                        "level": "Baja",
                        "patterns": ["Patrón agrupado"],
                        "title": "Contraseña no segura",
                        "explanation": (
                            "Los puntos presentan características compatibles "
                            "con un patrón agrupado."
                        ),
                    },
                }
            ]
        }
    )

    points: list[PointResponse]
    triangles: list[TriangleResponse]

    average_perimeter: float
    average_max_angle: float

    perimeter_test: PerimeterTestResponse
    angle_test: AngleTestResponse
    security: SecurityResponse