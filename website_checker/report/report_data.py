import copy
from dataclasses import asdict, dataclass
from dataclasses import field
from datetime import datetime
from typing import Any, Dict, List, Optional

from website_checker.analyze.result_data import StatusSummary
from website_checker.analyze.result_data import TestDescription


@dataclass
class ReportData:
    """Represents data for report generation."""

    url: str
    summary: List[StatusSummary] = field(default_factory=list)
    sitemap: List[Any] = field(default_factory=list)
    pages: List[Any] = field(default_factory=list)
    descriptions: List[TestDescription] = field(default_factory=list)
    screenshot: Optional[str] = None
    tags: Optional[List[str]] = None
    creation_date: datetime = field(default_factory=lambda: datetime.now())

    def to_dict(self) -> Dict[str, Any]:
        cp: Any = copy.deepcopy(self)
        cp.creation_date = self.creation_date.strftime("%d.%m.%Y %H:%M")
        return {k: v for k, v in asdict(cp).items() if v}
