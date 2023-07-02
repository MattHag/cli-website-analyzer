import os
from pathlib import Path

from automateda11y.pw.axerunner import AxeRunner
from automateda11y.pw.htmlcsrunner import HtmlCsRunner
from automateda11y.pw.settings import Settings
from playwright.sync_api import sync_playwright


def json_reports_dir():
    return Path(__file__).parent.parent.__str__()


def delete_images(directory):
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.lower().endswith((".png", ".jpg", ".jpeg", ".gif")):
                file_path = os.path.join(root, file)
                os.remove(file_path)


def run_a11y_checks_htmlcs(url):
    with sync_playwright() as p:
        Settings.report_dir = json_reports_dir() + "/reports"
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url)
        data = HtmlCsRunner(page).execute()
        browser.close()
        return data


def run_a11y_checks_deqaxe(url):
    with sync_playwright() as p:
        Settings.report_dir = json_reports_dir() + "/reports"
        browser = p.chromium.launch(headless=True)
        browser.timeout = 10000
        page = browser.new_page()
        page.goto(url)
        data = AxeRunner(page).execute()

        res = data

        path = Path("tmp")
        delete_images(path)

        for option in ["violations", "incomplete"]:
            print(f"{option.upper()}:")
            for idx, item in enumerate(getattr(res, option), start=1):
                print(f"{option} {idx}: {item.id}\n{item.description}\n{item.help}\n{item.helpUrl}")
                for outer, node in enumerate(item.nodes):
                    print(f"Msg {node.any[0].message}")
                    for inner, target in enumerate(node.target):
                        try:
                            # Wait for the element to be present
                            element = page.wait_for_selector(target)

                            # Get the bounding box of the element
                            bounding_box = element.bounding_box()

                            filename = path / f"screenshot-{option}-{idx}-{outer}-{inner}.png"
                            print(f"Saving screenshot to {filename}")
                            element.screenshot(path=filename)
                        except Exception as e:
                            print("Error:", e)
                            pass
            print()

        browser.close()
        return data


# Usage
url = ""
res = run_a11y_checks_deqaxe(url)

print(
    "Summary: \n"
    f"{len(res.incomplete)} Incomplete \n"
    f"{len(res.inapplicable)} Inapplicable\n"
    f"{len(res.violations)} Violations\n"
)
