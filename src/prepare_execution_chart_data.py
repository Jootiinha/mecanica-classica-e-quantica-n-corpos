import csv
from datetime import datetime
from pathlib import Path


INPUT_CSV = Path("outputs/performance_metrics.csv")
OUTPUT_TSV = Path("outputs/charts/execution_metrics_plot_data.tsv")


def build_execution_label(index: int, row: dict[str, str]) -> str:
    run_label = (row.get("run_label") or "").strip()
    timestamp = (row.get("timestamp_utc") or "").strip()
    base_label = run_label if run_label else timestamp
    return f"{index:02d} - {base_label}"


def parse_timestamp(row: dict[str, str]) -> datetime:
    timestamp = (row.get("timestamp_utc") or "").strip()
    return datetime.fromisoformat(timestamp)


def main():
    if not INPUT_CSV.exists():
        raise FileNotFoundError(f"Arquivo nao encontrado: {INPUT_CSV}")

    OUTPUT_TSV.parent.mkdir(parents=True, exist_ok=True)

    with INPUT_CSV.open("r", newline="", encoding="utf-8") as csv_file:
        rows = list(csv.DictReader(csv_file))

    rows.sort(key=parse_timestamp)

    with OUTPUT_TSV.open("w", newline="", encoding="utf-8") as tsv_file:
        writer = csv.writer(tsv_file, delimiter="\t")
        writer.writerow(
            [
                "execution_order",
                "execution_label",
                "wall_time_seconds",
                "cpu_time_seconds",
                "avg_cpu_percent",
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
                    row["avg_cpu_percent"],
                    row["peak_memory_mb"],
                ]
            )


if __name__ == "__main__":
    main()
