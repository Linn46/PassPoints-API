from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

from app.geometry.delaunay.validator import DelaunayValidationError


async def delaunay_validation_error_handler(
    request: Request, exc: DelaunayValidationError
) -> JSONResponse:
    """
    Handle DelaunayValidationError exceptions and return a user-friendly response.
    """
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "error": "Validation Error",
            "message": exc.message,
            "type": exc.validation_type,
            "details": exc.details,
        },
    )


async def request_validation_error_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """
    Return concise request validation errors without echoing submitted input.
    """
    errors = []
    for error in exc.errors():
        field_path = ".".join(str(x) for x in error["loc"])
        message = error["msg"]
        if message.startswith("Value error, "):
            message = message.removeprefix("Value error, ")

        errors.append({
            "field": field_path,
            "message": message,
            "type": error["type"],
        })

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        content={
            "error": "Request Validation Error",
            "message": "Invalid request data provided.",
            "errors": errors,
        },
    )
