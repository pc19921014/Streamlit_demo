import argparse
import re
from pathlib import Path

from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
from playwright.sync_api import sync_playwright


DEFAULT_URL = "http://localhost:8501"
DEFAULT_OUTPUT_DIR = "dashboard_screenshots"
DEFAULT_SYSTEMS = [
    "Condenser Tube Cleaning of Chillers",
    "Substation Heat Exchangers",
    "Chiller Motor Vibrations",
]


def slugify(value: str) -> str:
    value = value.strip().lower()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    return value.strip("-")


def wait_for_ui_settle(page, ms: int = 900) -> None:
    try:
        page.wait_for_load_state("networkidle", timeout=5000)
    except PlaywrightTimeoutError:
        # Streamlit can keep sockets open; timeout here is safe to ignore.
        pass
    page.wait_for_timeout(ms)


def click_segmented_option(page, group_idx: int, label: str) -> bool:
    groups = page.locator('[data-baseweb="button-group"]')
    if groups.count() <= group_idx:
        return False
    group = groups.nth(group_idx)
    button = group.get_by_role("button", name=label, exact=True)
    if button.count() == 0:
        button = group.locator("button", has_text=label).first
    if button.count() == 0:
        return False
    button.click()
    return True


def read_group_button_labels(page, group_idx: int) -> list[str]:
    groups = page.locator('[data-baseweb="button-group"]')
    if groups.count() <= group_idx:
        return []
    group = groups.nth(group_idx)
    buttons = group.locator("button")
    labels = []
    for i in range(buttons.count()):
        label = buttons.nth(i).inner_text().strip()
        if label:
            labels.append(label)
    return labels


def capture_dashboard_pages(url: str, output_dir: Path, systems: list[str], headless: bool) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=headless)
        page = browser.new_page(viewport={"width": 1920, "height": 1080})
        page.goto(url, wait_until="domcontentloaded")
        wait_for_ui_settle(page, ms=1500)

        screenshot_count = 0

        for system in systems:
            ok = click_segmented_option(page, group_idx=0, label=system)
            if not ok:
                print(f"[skip] System not found: {system}")
                continue
            wait_for_ui_settle(page)

            categories = read_group_button_labels(page, group_idx=1)
            if not categories:
                filename = output_dir / f"{screenshot_count:02d}_{slugify(system)}.png"
                page.screenshot(path=str(filename), full_page=True)
                screenshot_count += 1
                print(f"[saved] {filename}")
                continue

            for category in categories:
                clicked = click_segmented_option(page, group_idx=1, label=category)
                if not clicked:
                    print(f"[skip] Category not found: {system} -> {category}")
                    continue
                wait_for_ui_settle(page)

                filename = output_dir / (
                    f"{screenshot_count:02d}_{slugify(system)}__{slugify(category)}.png"
                )
                page.screenshot(path=str(filename), full_page=True)
                screenshot_count += 1
                print(f"[saved] {filename}")

        browser.close()
        print(f"\nDone. Captured {screenshot_count} screenshot(s) in: {output_dir}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Capture full-page screenshots for each dashboard page state."
    )
    parser.add_argument("--url", default=DEFAULT_URL, help="Dashboard URL")
    parser.add_argument(
        "--out",
        default=DEFAULT_OUTPUT_DIR,
        help="Output directory for screenshots",
    )
    parser.add_argument(
        "--headless",
        action="store_true",
        help="Run browser in headless mode",
    )
    parser.add_argument(
        "--systems",
        nargs="*",
        default=DEFAULT_SYSTEMS,
        help="System names to iterate over",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    capture_dashboard_pages(
        url=args.url,
        output_dir=Path(args.out),
        systems=args.systems,
        headless=args.headless,
    )


if __name__ == "__main__":
    main()
