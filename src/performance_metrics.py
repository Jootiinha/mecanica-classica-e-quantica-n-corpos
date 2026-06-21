import csv
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from time import perf_counter, process_time

try:
    import resource
except ImportError:  # pragma: no cover - unavailable on some non-Unix platforms
    resource = None


CSV_HEADERS = [
    "timestamp_utc",
    "run_label",
    "scenario_count",
    "wall_time_seconds",
    "cpu_time_seconds",
    "avg_cpu_percent",
    "peak_memory_mb",
]


@dataclass(frozen=True)
class ExecutionMetrics:
    scenario_count: int
    wall_time_seconds: float
    cpu_time_seconds: float
    avg_cpu_percent: float
    peak_memory_mb: float | None
    timestamp_utc: str
    run_label: str | None = None

    def to_csv_row(self):
        return [
            self.timestamp_utc,
            self.run_label or "",
            self.scenario_count,
            f"{self.wall_time_seconds:.6f}",
            f"{self.cpu_time_seconds:.6f}",
            f"{self.avg_cpu_percent:.2f}",
            f"{self.peak_memory_mb:.6f}" if self.peak_memory_mb is not None else "",
        ]


class ExecutionProfiler:
    def __init__(self):
        self._start_wall_time = perf_counter()
        self._start_cpu_time = process_time()

    def finish(self, scenario_count: int, run_label: str | None = None):
        wall_time_seconds = perf_counter() - self._start_wall_time
        cpu_time_seconds = process_time() - self._start_cpu_time
        avg_cpu_percent = (
            cpu_time_seconds / wall_time_seconds * 100 if wall_time_seconds > 0 else 0.0
        )

        return ExecutionMetrics(
            scenario_count=scenario_count,
            wall_time_seconds=wall_time_seconds,
            cpu_time_seconds=cpu_time_seconds,
            avg_cpu_percent=avg_cpu_percent,
            peak_memory_mb=_get_peak_memory_mb(),
            timestamp_utc=datetime.now(timezone.utc).isoformat(),
            run_label=run_label,
        )


def append_metrics_csv(output_dir: str | Path, metrics: ExecutionMetrics):
    csv_path = Path(output_dir) / "performance_metrics.csv"
    _ensure_csv_schema(csv_path)

    with csv_path.open("a", newline="", encoding="utf-8") as csv_file:
        writer = csv.writer(csv_file)

        writer.writerow(metrics.to_csv_row())

    return csv_path


def _ensure_csv_schema(csv_path: Path):
    if not csv_path.exists():
        with csv_path.open("w", newline="", encoding="utf-8") as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(CSV_HEADERS)
        return

    with csv_path.open("r", newline="", encoding="utf-8") as csv_file:
        rows = list(csv.reader(csv_file))

    if not rows:
        with csv_path.open("w", newline="", encoding="utf-8") as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(CSV_HEADERS)
        return

    current_header = rows[0]
    if current_header == CSV_HEADERS:
        return

    if current_header == [header for header in CSV_HEADERS if header != "run_label"]:
        migrated_rows = [CSV_HEADERS]
        for row in rows[1:]:
            migrated_rows.append(
                [
                    row[0] if len(row) > 0 else "",
                    "",
                    row[1] if len(row) > 1 else "",
                    row[2] if len(row) > 2 else "",
                    row[3] if len(row) > 3 else "",
                    row[4] if len(row) > 4 else "",
                    row[5] if len(row) > 5 else "",
                ]
            )

        with csv_path.open("w", newline="", encoding="utf-8") as csv_file:
            writer = csv.writer(csv_file)
            writer.writerows(migrated_rows)
        return

    raise ValueError(f"Cabecalho CSV inesperado em {csv_path}")


def _get_peak_memory_mb():
    if resource is None:
        return None

    max_rss = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    if sys.platform == "darwin":
        return max_rss / (1024 * 1024)
    return max_rss / 1024
