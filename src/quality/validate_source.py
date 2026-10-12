from pathlib import Path


def validate_source(path: str = "data/sample") -> int:
    """Ensure local development has at least one Parquet file."""
    files = list(Path(path).rglob("*.parquet"))
    if not files:
        raise FileNotFoundError(f"No Parquet files found under {path}")

    return len(files)


if __name__ == "__main__":
    file_count = validate_source()
    print(f"Found {file_count} Parquet file(s).")
