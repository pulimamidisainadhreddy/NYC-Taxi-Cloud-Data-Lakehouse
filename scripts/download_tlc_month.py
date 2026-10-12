from __future__ import annotations
import argparse
from pathlib import Path
from urllib.request import urlretrieve


def download(year: int, month: int, output_dir: str) -> Path:
    """Download one official TLC Yellow Taxi monthly Parquet file."""
    filename = f"yellow_tripdata_{year}-{month:02d}.parquet"
    url = f"https://d37ci6vzurychx.cloudfront.net/trip-data/{filename}"
    destination = Path(output_dir) / filename
    destination.parent.mkdir(parents=True, exist_ok=True)
    urlretrieve(url, destination)
    return destination


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--year", type=int, required=True)
    parser.add_argument("--month", type=int, required=True)
    parser.add_argument("--output-dir", default="data/sample")
    args = parser.parse_args()
    print(download(args.year, args.month, args.output_dir))
