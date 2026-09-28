import re

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from app.core.config.image_parameters import is_supported_image_size


class GraphicalPointInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    x: float = Field(ge=0, allow_inf_nan=False)
    y: float = Field(ge=0, allow_inf_nan=False)


class AuthRequestBase(BaseModel):
    model_config = ConfigDict(extra="forbid")

    username: str = Field(min_length=3, max_length=100)
    password: str = Field(min_length=1, max_length=128)
    image_id: str = Field(min_length=1, max_length=255)
    image_width: int = Field(gt=0)
    image_height: int = Field(gt=0)
    points: list[GraphicalPointInput] = Field(min_length=5, max_length=5)

    @field_validator("username", mode="before")
    @classmethod
    def normalize_username(cls, value: object) -> object:
        if not isinstance(value, str):
            return value
        normalized = value.strip().lower()
        if not re.fullmatch(r"[a-z0-9_.-]{3,100}", normalized):
            raise ValueError("Username may contain letters, digits, '.', '_' and '-'.")
        return normalized

    @field_validator("image_id")
    @classmethod
    def normalize_image_id(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("image_id must not be blank.")
        return normalized

    @model_validator(mode="after")
    def validate_graphical_selection(self) -> "AuthRequestBase":
        if not is_supported_image_size(self.image_width, self.image_height):
            raise ValueError("Unsupported image dimensions.")
        if any(
            point.x > self.image_width or point.y > self.image_height
            for point in self.points
        ):
            raise ValueError("Graphical points must be inside the image.")
        coordinates = [(point.x, point.y) for point in self.points]
        if len(set(coordinates)) != 5:
            raise ValueError("The five graphical points must be unique.")
        return self


class RegisterRequest(AuthRequestBase):
    password: str = Field(min_length=12, max_length=128)


class LoginRequest(AuthRequestBase):
    pass


class RegisteredUserResponse(BaseModel):
    id: str
    username: str


class AuthenticationResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: RegisteredUserResponse