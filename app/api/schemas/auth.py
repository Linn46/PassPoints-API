import re
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator
from app.core.config.image_parameters import is_supported_image_size

class PointInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    x: float = Field(ge=0, allow_inf_nan=False)
    y: float = Field(ge=0, allow_inf_nan=False)

class RegisterRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    username: str = Field(min_length=3, max_length=100)
    email: str = Field(min_length=5, max_length=254)
    image_id: str = Field(min_length=1, max_length=255)
    image_width: int = Field(gt=0)
    image_height: int = Field(gt=0)
    points: list[PointInput] = Field(min_length=5, max_length=5)

    @field_validator("username", mode="before")
    @classmethod
    def normalize_username(cls, value: object) -> object:
        if isinstance(value, str):
            value = value.strip().lower()
            if not re.fullmatch(r"[a-z0-9_.-]{3,100}", value):
                raise ValueError("Invalid username format.")
        return value

    @field_validator("email", mode="before")
    @classmethod
    def normalize_email(cls, value: object) -> object:
        if isinstance(value, str):
            value = value.strip().lower()
            if not re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", value):
                raise ValueError("A valid email address is required.")
        return value

    @field_validator("image_id")
    @classmethod
    def clean_image_id(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("image_id must not be blank.")
        return value

    @model_validator(mode="after")
    def validate_selection(self) -> "RegisterRequest":
        if not is_supported_image_size(self.image_width, self.image_height):
            raise ValueError("Unsupported image dimensions.")
        if any(p.x > self.image_width or p.y > self.image_height for p in self.points):
            raise ValueError("Points must be inside the image.")
        if len({(p.x, p.y) for p in self.points}) != 5:
            raise ValueError("The five points must be unique.")
        return self

class LoginRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    email: str = Field(min_length=5, max_length=254)
    image_id: str = Field(min_length=1, max_length=255)
    image_width: int = Field(gt=0)
    image_height: int = Field(gt=0)
    points: list[PointInput] = Field(min_length=5, max_length=5)

    @field_validator("email", mode="before")
    @classmethod
    def normalize_email(cls, value: object) -> object:
        if isinstance(value, str):
            value = value.strip().lower()
            if not re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", value):
                raise ValueError("A valid email address is required.")
        return value

    @field_validator("image_id")
    @classmethod
    def clean_image_id(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("image_id must not be blank.")
        return value

    @model_validator(mode="after")
    def validate_selection(self) -> "LoginRequest":
        if not is_supported_image_size(self.image_width, self.image_height):
            raise ValueError("Unsupported image dimensions.")
        if any(p.x > self.image_width or p.y > self.image_height for p in self.points):
            raise ValueError("Points must be inside the image.")
        if len({(p.x, p.y) for p in self.points}) != 5:
            raise ValueError("The five points must be unique.")
        return self

class UserResponse(BaseModel):
    id: str
    username: str
    email: str

class AuthenticationResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserResponse
