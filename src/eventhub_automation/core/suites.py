from dataclasses import dataclass


@dataclass(frozen=True)
class SuiteProfile:
    name: str
    description: str
    required_markers: frozenset[str] = frozenset()
    excluded_markers: frozenset[str] = frozenset({"quarantine"})

    def includes(self, keywords: set[str]) -> bool:
        return self.required_markers.issubset(keywords) and not self.excluded_markers.intersection(
            keywords
        )


SUITE_PROFILES = {
    "all": SuiteProfile("all", "All non-quarantined tests"),
    "smoke": SuiteProfile("smoke", "Critical smoke checks", frozenset({"smoke"})),
    "api-regression": SuiteProfile(
        "api-regression",
        "Full API regression",
        frozenset({"api"}),
        excluded_markers=frozenset({"e2e", "quarantine"}),
    ),
    "ui-regression": SuiteProfile(
        "ui-regression",
        "Full UI regression",
        excluded_markers=frozenset({"api", "quarantine"}),
    ),
    "e2e": SuiteProfile("e2e", "End-to-end user journeys", frozenset({"e2e"})),
    "release": SuiteProfile(
        "release",
        "Release confidence suite",
        excluded_markers=frozenset({"backend_gap", "flaky", "quarantine"}),
    ),
    "nightly": SuiteProfile("nightly", "Nightly non-quarantined regression"),
    "flaky-check": SuiteProfile(
        "flaky-check",
        "Known flaky tests for stability checks",
        frozenset({"flaky"}),
        excluded_markers=frozenset({"quarantine"}),
    ),
    "contract": SuiteProfile(
        "contract",
        "API schema and contract validation",
        frozenset({"contract"}),
    ),
    "visual": SuiteProfile("visual", "Visual regression screenshot checks", frozenset({"visual"})),
}


def suite_names() -> tuple[str, ...]:
    return tuple(sorted(SUITE_PROFILES))


def get_suite_profile(name: str) -> SuiteProfile:
    try:
        return SUITE_PROFILES[name]
    except KeyError as error:
        supported = ", ".join(suite_names())
        raise ValueError(f"Unsupported suite profile '{name}'. Use one of: {supported}") from error
