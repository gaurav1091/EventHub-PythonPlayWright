from dataclasses import dataclass


@dataclass(frozen=True)
class EnvironmentProfile:
    name: str
    base_url: str
    api_base_url: str


ENVIRONMENT_PROFILES = {
    "practice": EnvironmentProfile(
        name="practice",
        base_url="https://eventhub.rahulshettyacademy.com",
        api_base_url="https://api.eventhub.rahulshettyacademy.com",
    ),
    "qa": EnvironmentProfile(
        name="qa",
        base_url="https://eventhub.rahulshettyacademy.com",
        api_base_url="https://api.eventhub.rahulshettyacademy.com",
    ),
}


def environment_names() -> tuple[str, ...]:
    return tuple(sorted(ENVIRONMENT_PROFILES))


def get_environment_profile(name: str) -> EnvironmentProfile:
    try:
        return ENVIRONMENT_PROFILES[name]
    except KeyError as error:
        supported = ", ".join(environment_names())
        raise ValueError(f"Unsupported environment '{name}'. Use one of: {supported}") from error
