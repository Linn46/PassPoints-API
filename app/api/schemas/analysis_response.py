from pydantic import BaseModel


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


class AnalysisResponse(BaseModel):
    points: list[PointResponse]
    triangles: list[TriangleResponse]

    average_perimeter: float
    average_max_angle: float

    perimeter_test: PerimeterTestResponse
    angle_test: AngleTestResponse