"""Convert the HTML slide deck to a PDF (one 1920x1080 page per slide).

Uses a headless Chromium-based browser (Google Chrome or Microsoft Edge) that is already
installed, so it needs no extra Python packages. The deck's print stylesheet lays out every
slide as its own page.

Usage:
    python html_to_pdf.py                       # presentation.html -> presentation.pdf
    python html_to_pdf.py in.html -o out.pdf    # custom paths
    python html_to_pdf.py --browser "C:/path/to/chrome.exe"
"""

import argparse
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent

CANDIDATES = [
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
]
PATH_NAMES = ["chrome", "google-chrome", "google-chrome-stable", "chromium", "chromium-browser", "msedge"]


def find_browser(explicit: str | None) -> str:
    if explicit:
        if Path(explicit).exists():
            return explicit
        sys.exit(f"Browser not found: {explicit}")
    for path in CANDIDATES:
        if Path(path).exists():
            return path
    for name in PATH_NAMES:
        found = shutil.which(name)
        if found:
            return found
    sys.exit("No Chrome/Edge/Chromium found. Install one or pass --browser PATH.")


def count_pages(pdf: Path) -> int:
    data = pdf.read_bytes()
    return data.count(b"/Type /Page") - data.count(b"/Type /Pages")


def convert(html: Path, pdf: Path, browser: str, wait_ms: int) -> None:
    pdf.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as profile:
        cmd = [
            browser,
            "--headless=new",
            "--disable-gpu",
            "--no-first-run",
            "--no-default-browser-check",
            f"--user-data-dir={profile}",
            "--window-size=1920,1080",
            "--hide-scrollbars",
            "--no-pdf-header-footer",
            "--run-all-compositor-stages-before-draw",
            f"--virtual-time-budget={wait_ms}",  # lets web fonts load before printing
            f"--print-to-pdf={pdf}",
            html.as_uri(),
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
    if result.returncode != 0 or not pdf.exists():
        sys.stderr.write(result.stderr)
        sys.exit(f"PDF export failed (exit code {result.returncode}).")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("html", nargs="?", default=str(HERE / "presentation.html"))
    parser.add_argument("-o", "--output", default=None, help="output PDF (default: same name as the HTML)")
    parser.add_argument("--browser", default=None, help="path to chrome.exe / msedge.exe")
    parser.add_argument("--wait-ms", type=int, default=8000, help="time for fonts to load (ms)")
    args = parser.parse_args()

    html = Path(args.html).resolve()
    if not html.exists():
        sys.exit(f"HTML file not found: {html}")
    pdf = Path(args.output).resolve() if args.output else html.with_suffix(".pdf")
    if pdf.exists():
        os.remove(pdf)

    browser = find_browser(args.browser)
    print(f"Browser: {browser}")
    convert(html, pdf, browser, args.wait_ms)
    print(f"Saved {pdf} ({count_pages(pdf)} pages, {pdf.stat().st_size / 1024:.0f} KB)")


if __name__ == "__main__":
    main()
