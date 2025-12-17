"""Download and extract the MovieLens latest-small dataset."""
from __future__ import annotations

import argparse
import io
import zipfile
from pathlib import Path

import requests

MOVIELENS_URL = "https://files.grouplens.org/datasets/movielens/ml-latest-small.zip"


def download_file(url: str) -> bytes:
    response = requests.get(url, timeout=60)
    response.raise_for_status()
    return response.content


def extract_zip(raw_bytes: bytes, output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(io.BytesIO(raw_bytes)) as zf:
        zf.extractall(output_dir)


def main() -> None:
    parser = argparse.ArgumentParser(description="Download MovieLens latest-small dataset")
    parser.add_argument("--output", type=Path, default=Path("data/raw"), help="Directory to store raw files")
    args = parser.parse_args()

    print(f"Downloading MovieLens dataset from {MOVIELENS_URL} ...")
    raw_bytes = download_file(MOVIELENS_URL)
    print("Download complete. Extracting...")
    extract_zip(raw_bytes, args.output)
    print(f"Dataset extracted to {args.output.resolve()}")


if __name__ == "__main__":
    main()
