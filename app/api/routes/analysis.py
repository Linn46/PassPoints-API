from fastapi import APIRouter

from app.api.schemas.analysis_request import AnalysisRequest
from app.api.schemas.analysis_response import (
    AnalysisResponse,
    AngleTestResponse,
    PerimeterTestResponse,
    PointResponse,
    SecurityResponse,
    TriangleResponse,
)
from app.domain.point import Point
from app.application.analysis.service import AnalysisService


router = APIRouter(
    prefix="/analysis",
    tags=["Analysis"],
)

analysis_service = AnalysisService()


@router.post(
    "",
    response_model=AnalysisResponse,
)
def analyze(request: AnalysisRequest) -> AnalysisResponse:

    points = [
        Point(
            x=point.x,
            y=point.y,
        )
        for point in request.points
    ]

    result = analysis_service.analyze(
        points=points,
        image_width=request.image_width,
        image_height=request.image_height,
        alpha=request.alpha,
    )

    return AnalysisResponse(
        points=[
            PointResponse(
                x=point.x,
                y=point.y,
            )
            for point in points
        ],
        triangles=[
            TriangleResponse(
                vertices=[
                    PointResponse(
                        x=point.x,
                        y=point.y,
                    )
                    for point in triangle.vertices
                ]
            )
            for triangle in result.triangulation.triangles
        ],
        average_perimeter=result.average_perimeter,
        average_max_angle=result.average_max_angle,
        perimeter_test=PerimeterTestResponse(
            statistic=result.perimeter_test.statistic,
            critical_value=result.perimeter_test.critical_value,
            alpha=result.perimeter_test.alpha,
            reject_null=result.perimeter_test.reject_null,
        ),
        angle_test=AngleTestResponse(
            average_max_angle=result.angle_test.average_max_angle,
            statistic=result.angle_test.statistic,
            critical_value=result.angle_test.critical_value,
            alpha=result.angle_test.alpha,
            reject_null=result.angle_test.reject_null,
        ),
        security=SecurityResponse(
            is_weak=result.security.is_weak,
            level=result.security.level,
            patterns=result.security.patterns,
            title=result.security.title,
            explanation=result.security.explanation,
        ),
    )