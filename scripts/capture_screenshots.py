"""Capture screenshots of notebook HTML files using html2image or playwright."""
import sys
from pathlib import Path
import subprocess

REPO_ROOT = Path(__file__).resolve().parent.parent
NOTEBOOKS_DIR = REPO_ROOT / "notebooks"
SCREENSHOTS_DIR = REPO_ROOT / "submission" / "screenshots"
SCREENSHOTS_DIR.mkdir(exist_ok=True, parents=True)

def install_deps():
    print("Installing html2image...")
    subprocess.run([sys.executable, "-m", "pip", "install", "html2image"], check=True)

def main():
    try:
        from html2image import Html2Image
    except ImportError:
        install_deps()
        from html2image import Html2Image

    print("Initializing Html2Image...")
    hti = Html2Image()
    # Configure custom output path
    hti.output_path = str(SCREENSHOTS_DIR)

    notebooks = [
        ("01_embeddings_index.html", "nb1.png"),
        ("02_hybrid_search_rrf.html", "nb2.png"),
        ("03_search_api_benchmark.html", "nb3.png"),
        ("04_feast_feature_store.html", "nb4.png"),
    ]

    for html_name, img_name in notebooks:
        html_path = NOTEBOOKS_DIR / html_name
        if not html_path.exists():
            print(f"Error: {html_path} does not exist.")
            continue
        
        print(f"Capturing screenshot of {html_name} -> {img_name}...")
        try:
            # We pass the absolute file URL to avoid local file path parsing issues in Chrome
            url = html_path.as_uri()
            hti.screenshot(url=url, save_as=img_name, size=(1200, 1600))
            print(f"Saved {img_name}")
        except Exception as e:
            print(f"Failed to capture {html_name}: {e}")

if __name__ == "__main__":
    main()
