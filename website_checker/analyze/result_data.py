from dataclasses import dataclass


@dataclass
class TestDescription:
    title: str
    description: str


@dataclass
class StatusSummary:
    title: str
    status: str
