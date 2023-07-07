import base64
import json
from dataclasses import dataclass
from itertools import groupby
from pathlib import Path

from automateda11y.pw.modal.axe.issues import Issues
from marshmallow import EXCLUDE

from website_checker.crawl.axe.parameters import Parameters, Standard


@dataclass
class AxeIssue:
    id: str
    impact: str
    target: str
    screenshot: str
    # html: str
    # description: str
    help: str
    help_url: str


class Axe:
    def __init__(self):
        self.settings = Parameters()

    def configure(self, params: Parameters):
        self.settings = params

    def run_check(self, page) -> Issues:
        page.wait_for_load_state("domcontentloaded")
        axe_file = Path() / "crawl" / "axe" / "resources" / "axe.js"
        js_text = axe_file.read_text()

        page.evaluate("async (js)=> await window.eval(js)", js_text)
        data = page.evaluate("async (param) => await axeData(param)", self.settings.to_json())

        Path("axe_data.json").write_text(json.dumps(data, indent=4))
        return Issues.Schema().load(data, unknown=EXCLUDE)

    def evaluate(self, page, result: Issues) -> list[AxeIssue]:
        """Evaluates the axe data and returns a list of violations."""
        violations = result.violations
        inapplicable = result.inapplicable
        incomplete = result.incomplete

        print(f"Standard: {result.testEngine} {result.testRunner}")
        print(f"Options: {result.toolOptions}")

        print(f"Violations: {len(violations)}")
        print(f"Inapplicable: {len(inapplicable)}")
        print(f"Incomplete: {len(incomplete)}")
        print(f"Total: {len(violations) + len(inapplicable) + len(incomplete)}")

        issues = []
        issues.extend(violations)

        results = []
        for issue in issues:
            print(issue.description)
            print(issue.id)
            print(len(issue.nodes))

            # group_objects_by_severity(issue_type.nodes)
            for node in issue.nodes:
                print(f"{node.impact.upper()} Target: {node.target} {node.html}")

                # for checks in node.any:
                target = node.target[0]
                screenshot = ""
                try:
                    element = page.wait_for_selector(target, timeout=2000)
                    encoded_image = element.screenshot()
                    screenshot = base64.b64encode(encoded_image).decode()
                except (TimeoutError, IndexError) as e:
                    print(e)
                except Exception as e:
                    print(e)

                axe_issue = AxeIssue(
                    id=issue.id,
                    impact=node.impact or issue.impact,
                    target=target,
                    help=issue.help,
                    help_url=issue.helpUrl,
                    screenshot=screenshot,
                )
                results.append(axe_issue)
        return results


def group_objects_by_severity(object_list):
    sorted_list = sorted(object_list, key=lambda obj: obj.impact)
    grouped = groupby(sorted_list, key=lambda obj: obj.impact)
    result = {key: list(group) for key, group in grouped}
    for item in result.items():
        print(f"{item[0]}: {len(item[1])}")
    return result
