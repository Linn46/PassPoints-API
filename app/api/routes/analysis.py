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


def _single_response(
    points,
    request: AnalysisRequest,
    result,
) -> AnalysisResponse:
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


def _aggregate_security(results):
    patterns = []
    for result in results:
        for pattern in result.security.patterns:
            if pattern not in patterns:
                patterns.append(pattern)

    is_weak = any(result.security.is_weak for result in results)
    level = "Baja" if is_weak else "Alta"
    title = "Contraseña no segura" if is_weak else "Contraseña sin patrón débil detectado"
    explanation_parts = [
        f"{result.method}: {result.security.explanation}"
        for result in results
        if getattr(result, "security", None) is not None
    ]

    return SecurityResponse(
        is_weak=is_weak,
        level=level,
        patterns=patterns,
        title=title,
        explanation=" ".join(explanation_parts) if explanation_parts else "Sin explicación disponible.",
    )


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

    selected_methods = list(request.methods or [request.method] or ["delaunay_statistical"])
    results = []
    for method_name in selected_methods:
        result = analysis_service.analyze(
            points=points,
            image_width=request.image_width,
            image_height=request.image_height,
            alpha=request.alpha,
            method=method_name,
        )
        results.append(result)

    if len(results) == 1:
        result = results[0]
        if getattr(result, "method", None) == "mean_distance_convex_hull":
            security = result.security
            return AnalysisResponse(
                points=[
                    PointResponse(
                        x=point.x,
                        y=point.y,
                    )
                    for point in points
                ],
                triangles=[],
                average_perimeter=0.0,
                average_max_angle=0.0,
                perimeter_test=PerimeterTestResponse(
                    statistic=0.0,
                    critical_value=0.0,
                    alpha=request.alpha,
                    reject_null=False,
                ),
                angle_test=AngleTestResponse(
                    average_max_angle=0.0,
                    statistic=0.0,
                    critical_value=0.0,
                    alpha=request.alpha,
                    reject_null=False,
                ),
                security=SecurityResponse(
                    is_weak=security.is_weak,
                    level=security.level,
                    patterns=security.patterns,
                    title=security.title,
                    explanation=security.explanation,
                ),
            )
        return _single_response(points, request, result)

    delaunay_result = next((result for result in results if getattr(result, "method", None) == "delaunay_statistical"), results[0])
    combined_security = _aggregate_security(results)

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
            for triangle in delaunay_result.triangulation.triangles
        ],
        average_perimeter=delaunay_result.average_perimeter,
        average_max_angle=delaunay_result.average_max_angle,
        perimeter_test=PerimeterTestResponse(
            statistic=delaunay_result.perimeter_test.statistic,
            critical_value=delaunay_result.perimeter_test.critical_value,
            alpha=delaunay_result.perimeter_test.alpha,
            reject_null=delaunay_result.perimeter_test.reject_null,
        ),
        angle_test=AngleTestResponse(
            average_max_angle=delaunay_result.angle_test.average_max_angle,
            statistic=delaunay_result.angle_test.statistic,
            critical_value=delaunay_result.angle_test.critical_value,
            alpha=delaunay_result.angle_test.alpha,
            reject_null=delaunay_result.angle_test.reject_null,
        ),
        security=combined_security,
    )