import os
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Settings:
	"""Configuración de ejecución de la API."""

	app_name: str = "Passpoints Weak Password Detection API"
	app_version: str = "1.0.0"
	host: str = "0.0.0.0"
	port: int = 8000

	@classmethod
	def from_environment(cls) -> "Settings":
		"""Construye la configuración usando variables de entorno opcionales."""
		defaults = cls()
		return cls(
			app_name=os.getenv("PASSPOINTS_APP_NAME", defaults.app_name),
			app_version=os.getenv("PASSPOINTS_APP_VERSION", defaults.app_version),
			host=os.getenv("PASSPOINTS_HOST", defaults.host),
			port=int(os.getenv("PASSPOINTS_PORT", str(defaults.port))),
		)


settings = Settings.from_environment()
