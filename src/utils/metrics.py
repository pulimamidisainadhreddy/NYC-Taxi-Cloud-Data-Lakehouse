from __future__ import annotations
from dataclasses import asdict, dataclass
from datetime import datetime, timezone


@dataclass
class PipelineMetrics:
    """Run-level pipeline metrics."""

    run_id: str
    input_records: int = 0
    output_records: int = 0
    rejected_records: int = 0
    duplicate_records: int = 0
    status: str = "RUNNING"
    started_at: str = ""
    finished_at: str = ""

    def start(self) -> None:
        self.started_at = datetime.now(timezone.utc).isoformat()

    def finish(self, status: str) -> None:
        self.status = status
        self.finished_at = datetime.now(timezone.utc).isoformat()

    def as_dict(self) -> dict:
        return asdict(self)
