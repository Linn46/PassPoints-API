from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

AnalysisMethod = Literal["delaunay_statistical", "mean_distance_convex_hull"]


class PointRequest(BaseModel):
    x: float = Field(..., description="Coordenada X del punto.")
    y: float = Field(..., description="Coordenada Y del punto.")


class AnalysisRequest(BaseModel):
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
                    "image_width": 1920,
                    "image_height": 1080,
                    "alpha": 0.05,
                    "method": "delaunay_statistical",
                }
            ]
        }
    )

    points: list[PointRequest] = Field(
        ...,
        min_length=5,
        max_length=5,
        description="Los cinco puntos de la contraseña Passpoint.",
    )

    image_width: int = Field(
        ...,
        gt=0,
        description="Ancho de la imagen en píxeles.",
    )

    image_height: int = Field(
        ...,
        gt=0,
        description="Alto de la imagen en píxeles.",
    )

    alpha: float = Field(
        default=0.05,
        gt=0,
        lt=1,
        description="Nivel de significación estadística.",
    )

    method: AnalysisMethod | None = Field(
        default=None,
        description="Metodología de análisis a ejecutar (compatibilidad).",
    )

    methods: list[AnalysisMethod] | None = Field(
        default=None,
        description="Metodologías de análisis a ejecutar. Se puede elegir una o varias.",
    )

    @model_validator(mode="after")
    def validate_coordinates(self):
        for point in self.points:
            if not 0 <= point.x <= self.image_width:
                raise ValueError(
                    f"Point x={point.x} is outside the image."
                )

            if not 0 <= point.y <= self.image_height:
                raise ValueError(
                    f"Point y={point.y} is outside the image."
                )

        if self.methods is None:
            if self.method is not None:
                self.methods = [self.method]
            else:
                self.methods = ["delaunay_statistical"]

        if self.method is not None and self.method not in self.methods:
            self.methods = [self.method, *self.methods]

        unique_methods: list[AnalysisMethod] = []
        for method_name in self.methods:
            if method_name not in unique_methods:
                unique_methods.append(method_name)
        self.methods = unique_methods

        if not self.methods:
            self.methods = ["delaunay_statistical"]

        return self