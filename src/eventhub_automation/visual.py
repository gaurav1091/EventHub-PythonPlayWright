from pathlib import Path

import allure
from PIL import Image, ImageChops
from playwright.sync_api import Page

DEFAULT_MAX_DIFF_RATIO = 0.01
DEFAULT_PIXEL_THRESHOLD = 20


def assert_visual_baseline(
    page: Page,
    baseline_path: Path | str,
    actual_path: Path | str,
    *,
    full_page: bool = True,
    max_diff_ratio: float = DEFAULT_MAX_DIFF_RATIO,
    pixel_threshold: int = DEFAULT_PIXEL_THRESHOLD,
) -> None:
    baseline_path = Path(baseline_path)
    actual_path = Path(actual_path)
    actual_path.parent.mkdir(parents=True, exist_ok=True)
    screenshot = page.screenshot(path=str(actual_path), full_page=full_page, animations="disabled")

    if not baseline_path.exists():
        raise AssertionError(
            f"Missing visual baseline: {baseline_path}. "
            f"Create it intentionally from the reviewed actual image: {actual_path}."
        )

    expected = baseline_path.read_bytes()
    expected_image = Image.open(baseline_path).convert("RGB")
    actual_image = Image.open(actual_path).convert("RGB")

    if expected_image.size != actual_image.size:
        _attach_visual_images(baseline_path, expected, screenshot)
        raise AssertionError(
            f"Visual baseline size mismatch for {baseline_path}: "
            f"expected {expected_image.size}, actual {actual_image.size}"
        )

    diff_ratio = _changed_pixel_ratio(expected_image, actual_image, pixel_threshold)
    if diff_ratio > max_diff_ratio:
        _attach_visual_images(baseline_path, expected, screenshot)
        diff_image = ImageChops.difference(expected_image, actual_image)
        diff_path = actual_path.with_name(f"{actual_path.stem}-diff.png")
        diff_image.save(diff_path)
        allure.attach.file(
            str(diff_path),
            name=f"{baseline_path.stem}-diff",
            attachment_type=allure.attachment_type.PNG,
        )
        raise AssertionError(
            f"Visual baseline mismatch for {baseline_path}: "
            f"{diff_ratio:.2%} changed pixels exceeds {max_diff_ratio:.2%}"
        )


def _changed_pixel_ratio(
    expected_image: Image.Image,
    actual_image: Image.Image,
    threshold: int,
) -> float:
    diff = ImageChops.difference(expected_image, actual_image)
    changed_pixels = 0
    rgb_bytes = diff.tobytes()
    for index in range(0, len(rgb_bytes), 3):
        if max(rgb_bytes[index : index + 3]) > threshold:
            changed_pixels += 1
    return changed_pixels / (expected_image.width * expected_image.height)


def _attach_visual_images(baseline_path: Path, expected: bytes, actual: bytes) -> None:
    allure.attach(
        expected,
        name=f"{baseline_path.stem}-expected",
        attachment_type=allure.attachment_type.PNG,
    )
    allure.attach(
        actual,
        name=f"{baseline_path.stem}-actual",
        attachment_type=allure.attachment_type.PNG,
    )
