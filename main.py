import os

import numpy as np

from src.performance_metrics import ExecutionProfiler, append_metrics_csv
from src.simulacao import simular_dois_corpos_3d
from src.utils import (
    build_metrics_output_dir,
    build_results_file_path_for_formalism,
    load_scenarios,
)

PATH_SCENARIOS = './scenarios/'
FORMALISM = "newtonian"


def run_simulation():
    scenario_file = os.environ.get('SCENARIO')
    if not scenario_file:
        raise ValueError("A variavel de ambiente SCENARIO precisa ser informada.")

    scenario_config = load_scenarios(PATH_SCENARIOS + scenario_file)
    run_label = os.environ.get("RUN_LABEL")

    profiler = ExecutionProfiler()
    result = simular_dois_corpos_3d(scenario_config, formalism=FORMALISM)
    metrics = profiler.finish(run_label=run_label)

    results_path = build_results_file_path_for_formalism(scenario_file, FORMALISM)
    metrics_output_dir = build_metrics_output_dir(FORMALISM)

    results_path.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(results_path, **result)
    csv_path = append_metrics_csv(metrics_output_dir, metrics)

    print(f"[{FORMALISM}] Resultados fisicos salvos em: {results_path}")
    print(f"[{FORMALISM}] Metricas salvas em: {csv_path}")
    print(f"[{FORMALISM}] Tempo total: {metrics.wall_time_seconds:.3f}s")
    print(f"[{FORMALISM}] Tempo de CPU: {metrics.cpu_time_seconds:.3f}s")
    print(f"[{FORMALISM}] CPU medio do processo: {metrics.avg_process_cpu_percent:.2f}%")
    if metrics.avg_machine_cpu_percent is not None:
        print(f"[{FORMALISM}] CPU media da maquina: {metrics.avg_machine_cpu_percent:.2f}%")
    if metrics.peak_memory_mb is not None:
        print(f"[{FORMALISM}] Pico de memoria: {metrics.peak_memory_mb:.3f} MB")

    return [(FORMALISM, results_path, csv_path, metrics)]


if __name__ == "__main__":
    os.makedirs("outputs", exist_ok=True)
    run_simulation()
