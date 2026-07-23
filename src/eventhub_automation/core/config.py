from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    base_url: str = Field(
        default="https://eventhub.rahulshettyacademy.com",
        alias="EVENTHUB_BASE_URL",
    )
    api_base_url: str = Field(
        default="https://api.eventhub.rahulshettyacademy.com",
        alias="EVENTHUB_API_BASE_URL",
    )
    user_email: str = Field(default="", alias="EVENTHUB_USER_EMAIL")
    user_password: str = Field(default="", alias="EVENTHUB_USER_PASSWORD", repr=False)
    browser: str = Field(default="chromium", alias="BROWSER")
    headless: bool = Field(default=True, alias="HEADLESS")
    slow_mo_ms: int = Field(default=0, alias="SLOW_MO_MS")
