import json
from enum import Enum


class Standard(Enum):
    WCAG2AA = "wcag2aa"
    WCAG21A = "wcag21a"
    WCAG21AA = "wcag21aa"
    WCAG21AAA = "wcag21aaa"
    BEST_PRACTICE = "best-practice"


class Parameters:
    def __init__(self, standard: Standard = Standard.WCAG21AA):
        self.ignoreCodes = []
        self.standard = standard.value

    def set_standard(self, standard: Standard):
        self.standard = standard.value

    def set_ignore_codes(self, ignore_codes):
        self.ignoreCodes = ignore_codes

    def to_json(self):
        return json.dumps(self.__dict__)
