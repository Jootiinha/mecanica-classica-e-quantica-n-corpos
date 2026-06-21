import csv
import os
from datetime import datetime
from pathlib import Path

from src.utils import build_chart_data_file_path, build_metrics_output_dir


def _resolve_formalism() -> str:
    return (os.environ.get("FORMALISM") or "newtonian").strip().lower()


def build_execution_label(index: int, row: dict[str, str]) -> str:
    run_label = (row.get("run_label") or "").strip()
    timestamp = (row.get("timestamp_utc") or "").strip()
    base_label = run_label if run_label else timestamp
    return f"{index:02d} - {base_label}"


def parse_timestamp(row: dict[str, str]) -> datetime:
    timestamp = (row.get("timestamp_utc") or "").strip()
    return datetime.fromisoformat(timestamp)


def main():
    formalism = _resolve_formalism()
    input_csv = build_metrics_output_dir(formalism) / "performance_metrics.csv"
    output_tsv = build_chart_data_file_path(formalism)

    if not input_csv.exists():
        raise FileNotFoundError(f"Arquivo nao encontrado: {input_csv}")

    output_tsv.parent.mkdir(parents=True, exist_ok=True)

    with input_csv.open("r", newline="", encoding="utf-8") as csv_file:
        rows = list(csv.DictReader(csv_file))

    rows.sort(key=parse_timestamp)

    with output_tsv.open("w", newline="", encoding="utf-8") as tsv_file:
        writer = csv.writer(tsv_file, delimiter="\t")
        writer.writerow(
            [
                "execution_order",
                "execution_label",
                "wall_time_seconds",
                "cpu_time_seconds",
                "avg_process_cpu_percent",
                "avg_machine_cpu_percent",
                "peak_memory_mb",
            ]
        )

        for index, row in enumerate(rows, start=1):
            writer.writerow(
                [
                    index,
                    build_execution_label(index, row),
                    row["wall_time_seconds"],
                    row["cpu_time_seconds"],
                    row.get("avg_process_cpu_percent", row.get("avg_cpu_percent", "")),
                    row.get("avg_machine_cpu_percent", ""),
                    row["peak_memory_mb"],
                ]
            )


if __name__ == "__main__":
    main()
