import re
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator
from app.core.config.image_parameters import is_supported_image_size

_EMAIL_PATTERN = re.compile(
    r"[A-Z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[A-Z0-9!#$%&'*+/=?^_`{|}~-]+)*"
    r"@[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?"
    r"(?:\.[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?)*\.[A-Z]{2,63}",
    re.IGNORECASE,
)

def _normalize_email(value: object) -> object:
    if isinstance(value, str):
        value = value.strip().lower()
        if len(value) > 254 or not _EMAIL_PATTERN.fullmatch(value):
            raise ValueError("A valid email address is required.")
    return value

class PointInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    x: float = Field(ge=0, allow_inf_nan=False)
    y: float = Field(ge=0, allow_inf_nan=False)

GraphicalPointInput = PointInput

class RegisterRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    username: str = Field(min_length=3, max_length=100)
    email: str = Field(min_length=5, max_length=254)
    image_id: str = Field(min_length=1, max_length=255)
    image_width: int = Field(gt=0)
    image_height: int = Field(gt=0)
    points: list[PointInput] = Field(min_length=5, max_length=5)
    confirmation_points: list[list[PointInput]] | None = Field(
        default=None,
        min_length=2,
        max_length=2,
    )
    repetition_count: int | None = Field(default=None, ge=2)
    tolerance_grid_divisions: int = Field(default=5, ge=1, le=5)

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
        return _normalize_email(value)

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
        if self.confirmation_points is not None:
            if len(self.confirmation_points) != 2:
                raise ValueError("Exactly two confirmation point sequences are required.")
            for confirmation in self.confirmation_points:
                if len(confirmation) != 5:
                    raise ValueError("Each confirmation sequence must have exactly 5 points.")
                if any(p.x > self.image_width or p.y > self.image_height for p in confirmation):
                    raise ValueError("Confirmation points must be inside the image.")
                if len({(p.x, p.y) for p in confirmation}) != 5:
                    raise ValueError("The five points in each confirmation must be unique.")
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
        return _normalize_email(value)

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

class LoginImagesRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    email: str = Field(min_length=5, max_length=254)
    image_ids: list[str] = Field(min_length=1, max_length=100)

    @field_validator("email", mode="before")
    @classmethod
    def normalize_email(cls, value: object) -> object:
        return _normalize_email(value)

    @field_validator("image_ids")
    @classmethod
    def clean_image_ids(cls, values: list[str]) -> list[str]:
        cleaned = [value.strip() for value in values]
        if any(not value or len(value) > 255 for value in cleaned):
            raise ValueError("Image IDs must be non-blank and at most 255 characters.")
        return cleaned

class UserResponse(BaseModel):
    id: str
    username: str
    email: str

class AuthenticationResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserResponse

class LoginImagesResponse(BaseModel):
    image_ids: list[str] = Field(min_length=3, max_length=3)
