from collections.abc import Iterable
from typing import Any, TypeVar

from pydantic import BaseModel
from requests import Response

from eventhub_automation.api.models import ApiEnvelope

ModelT = TypeVar("ModelT", bound=BaseModel)


def assert_status(response: Response, expected_status: int) -> dict[str, Any]:
    assert response.status_code == expected_status, response.text
    return response.json()


def assert_success(response: Response, expected_status: int = 200) -> dict[str, Any]:
    body = assert_status(response, expected_status)
    assert body["success"] is True
    return body


def assert_error(
    response: Response,
    expected_status: int,
    expected_error: str | None = None,
) -> dict[str, Any]:
    body = assert_status(response, expected_status)
    assert body["success"] is False
    if expected_error is not None:
        assert body["error"] == expected_error
    return body


def assert_error_contains(response: Response, expected_status: int, text: str) -> dict[str, Any]:
    body = assert_error(response, expected_status)
    assert text.lower() in body["error"].lower()
    return body


def assert_validation_error(
    response: Response,
    expected_fields: Iterable[str],
) -> dict[str, Any]:
    body = assert_error(response, 400, "Validation failed")
    error_fields = {detail["field"] for detail in body["details"]}
    assert set(expected_fields).issubset(error_fields)
    return body


def parse_envelope(response: Response, expected_status: int | None = None) -> ApiEnvelope:
    if expected_status is not None:
        assert response.status_code == expected_status, response.text
    return ApiEnvelope.model_validate(response.json())


def parse_data(response: Response, model: type[ModelT], expected_status: int = 200) -> ModelT:
    body = assert_success(response, expected_status)
    return model.model_validate(body["data"])


def parse_data_list(
    response: Response,
    model: type[ModelT],
    expected_status: int = 200,
) -> list[ModelT]:
    body = assert_success(response, expected_status)
    return [model.model_validate(item) for item in body["data"]]
