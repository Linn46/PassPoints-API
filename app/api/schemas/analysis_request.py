from pydantic import BaseModel, Field, model_validator


class PointRequest(BaseModel):
    x: float = Field(..., description="Coordenada X del punto.")
    y: float = Field(..., description="Coordenada Y del punto.")


class AnalysisRequest(BaseModel):
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

        return self