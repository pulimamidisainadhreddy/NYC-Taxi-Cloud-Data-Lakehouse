from pathlib import Path


def validate_output(path: str = "local-lake/silver") -> None:
    """Verify Silver output exists."""
    if not Path(path).exists():
        raise FileNotFoundError(f"Missing Silver output: {path}")


if __name__ == "__main__":
    validate_output()
