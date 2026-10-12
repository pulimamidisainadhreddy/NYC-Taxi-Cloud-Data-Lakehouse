from pathlib import Path


def test_required_directories_exist() -> None:
    for directory in ["dags", "src", "dbt", "tests", "sql", "docs", "config"]:
        assert Path(directory).exists()
