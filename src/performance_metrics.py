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

try:
    import psutil
except ImportError:  # pragma: no cover - dependency may be unavailable before install
    psutil = None


CSV_HEADERS = [
    "timestamp_utc",
    "run_label",
    "wall_time_seconds",
    "cpu_time_seconds",
    "avg_process_cpu_percent",
    "avg_machine_cpu_percent",
    "peak_memory_mb",
]


@dataclass(frozen=True)
class ExecutionMetrics:
    wall_time_seconds: float
    cpu_time_seconds: float
    avg_process_cpu_percent: float
    avg_machine_cpu_percent: float | None
    peak_memory_mb: float | None
    timestamp_utc: str
    run_label: str | None = None

    def to_csv_row(self):
        return [
            self.timestamp_utc,
            self.run_label or "",
            f"{self.wall_time_seconds:.6f}",
            f"{self.cpu_time_seconds:.6f}",
            f"{self.avg_process_cpu_percent:.2f}",
            f"{self.avg_machine_cpu_percent:.2f}" if self.avg_machine_cpu_percent is not None else "",
            f"{self.peak_memory_mb:.6f}" if self.peak_memory_mb is not None else "",
        ]


class ExecutionProfiler:
    def __init__(self):
        self._start_wall_time = perf_counter()
        self._start_cpu_time = process_time()
        self._start_machine_cpu_times = _get_machine_cpu_times()

    def finish(self, run_label: str | None = None):
        wall_time_seconds = perf_counter() - self._start_wall_time
        cpu_time_seconds = process_time() - self._start_cpu_time
        avg_process_cpu_percent = (
            cpu_time_seconds / wall_time_seconds * 100 if wall_time_seconds > 0 else 0.0
        )
        avg_machine_cpu_percent = _calculate_avg_machine_cpu_percent(self._start_machine_cpu_times)

        return ExecutionMetrics(
            wall_time_seconds=wall_time_seconds,
            cpu_time_seconds=cpu_time_seconds,
            avg_process_cpu_percent=avg_process_cpu_percent,
            avg_machine_cpu_percent=avg_machine_cpu_percent,
            peak_memory_mb=_get_peak_memory_mb(),
            timestamp_utc=datetime.now(timezone.utc).isoformat(),
            run_label=run_label,
        )


def append_metrics_csv(output_dir: str | Path, metrics: ExecutionMetrics):
    csv_path = Path(output_dir) / "performance_metrics.csv"
    csv_path.parent.mkdir(parents=True, exist_ok=True)
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

    if current_header == ["timestamp_utc", "scenario_count", "wall_time_seconds", "cpu_time_seconds", "avg_cpu_percent", "peak_memory_mb"]:
        migrated_rows = [CSV_HEADERS]
        for row in rows[1:]:
            migrated_rows.append(
                [
                    row[0] if len(row) > 0 else "",
                    "",
                    row[2] if len(row) > 2 else "",
                    row[3] if len(row) > 3 else "",
                    row[4] if len(row) > 4 else "",
                    "",
                    row[5] if len(row) > 5 else "",
                ]
            )

        with csv_path.open("w", newline="", encoding="utf-8") as csv_file:
            writer = csv.writer(csv_file)
            writer.writerows(migrated_rows)
        return

    if current_header == [
        "timestamp_utc",
        "run_label",
        "scenario_count",
        "wall_time_seconds",
        "cpu_time_seconds",
        "avg_cpu_percent",
        "peak_memory_mb",
    ]:
        migrated_rows = [CSV_HEADERS]
        for row in rows[1:]:
            migrated_rows.append(
                [
                    row[0] if len(row) > 0 else "",
                    row[1] if len(row) > 1 else "",
                    row[3] if len(row) > 3 else "",
                    row[4] if len(row) > 4 else "",
                    row[5] if len(row) > 5 else "",
                    "",
                    row[6] if len(row) > 6 else "",
                ]
            )

        with csv_path.open("w", newline="", encoding="utf-8") as csv_file:
            writer = csv.writer(csv_file)
            writer.writerows(migrated_rows)
        return

    if current_header == [
        "timestamp_utc",
        "run_label",
        "wall_time_seconds",
        "cpu_time_seconds",
        "avg_cpu_percent",
        "peak_memory_mb",
    ]:
        migrated_rows = [CSV_HEADERS]
        for row in rows[1:]:
            migrated_rows.append(
                [
                    row[0] if len(row) > 0 else "",
                    row[1] if len(row) > 1 else "",
                    row[2] if len(row) > 2 else "",
                    row[3] if len(row) > 3 else "",
                    row[4] if len(row) > 4 else "",
                    "",
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


def _get_machine_cpu_times():
    if psutil is None:
        return None
    return psutil.cpu_times()


def _calculate_avg_machine_cpu_percent(start_cpu_times) -> float | None:
    if psutil is None or start_cpu_times is None:
        return None

    end_cpu_times = psutil.cpu_times()
    start_values = start_cpu_times._asdict()
    end_values = end_cpu_times._asdict()
    common_fields = set(start_values) & set(end_values)

    total_delta = sum(end_values[field] - start_values[field] for field in common_fields)
    idle_fields = {"idle", "iowait"} & common_fields
    idle_delta = sum(end_values[field] - start_values[field] for field in idle_fields)

    if total_delta <= 0:
        return None

    busy_delta = total_delta - idle_delta
    return max(0.0, min(100.0, busy_delta / total_delta * 100))
