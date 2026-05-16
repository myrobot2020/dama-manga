#!/usr/bin/env python3
"""
Manga Pipeline Orchestrator (Numbered Step -01)
Combines: Depanel -> Segment -> Describe -> Score/Map
"""

import subprocess
import sys
from pathlib import Path

def run_step(name: str, cmd: list[str]):
    print(f"\n{'='*20}")
    print(f"🚀 [MANGA PIPELINE] STEP: {name}")
    print(f"{'='*20}")
    try:
        subprocess.run(cmd, check=True)
        print(f"✅ {name} Completed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"❌ {name} Failed with exit code {e.returncode}")
        sys.exit(e.returncode)

def main():
    # 1. DEPANEL: Extract panels from PDFs
    run_step("DEPANEL", ["python", "scripts/manga/bulk_depanel.py"])

    # 2. SEGMENT: OCR & Categorize into Text vs No-Text
    run_step("SEGMENT", ["python", "scripts/manga/classify_manga_panels.py"])

    # 3. DESCRIBE: Vision analysis (Vision Model -> Suttic Stylist)
    run_step("DESCRIBE", ["python", "scripts/manga/describe_vol1.py"])

    # 4. SCORE & MAP: Final mapping of panels to Sutta IDs
    run_step("SCORE/MAP", ["python", "scripts/manga/map_panels.py"])

    print("\n✨ Manga Pipeline Finished. Bones extracted, described, and mapped.")

if __name__ == "__main__":
    main()
