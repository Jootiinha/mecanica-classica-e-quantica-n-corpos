import os

import numpy as np

from src.performance_metrics import ExecutionProfiler, append_metrics_csv
from src.simulacao import simular_dois_corpos_3d
from src.utils import build_results_file_path, load_scenarios

PATH_SCENARIOS = './scenarios/'


def run_simulation():
    scenario_file = os.environ.get('SCENARIO')
    if not scenario_file:
        raise ValueError("A variavel de ambiente SCENARIO precisa ser informada.")

    scenario_config = load_scenarios(PATH_SCENARIOS + scenario_file)
    simulation_result = simular_dois_corpos_3d(scenario_config)
    results_path = build_results_file_path(scenario_file)
    results_path.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(results_path, **simulation_result)

    print(f"Resultados fisicos salvos em: {results_path}")
    return results_path


if __name__ == "__main__":
    os.makedirs("outputs", exist_ok=True)
    run_label = os.environ.get("RUN_LABEL")
    profiler = ExecutionProfiler()

    run_simulation()

    metrics = profiler.finish(run_label=run_label)
    caminho_csv = append_metrics_csv("outputs", metrics)

    print(f"Métricas salvas em: {caminho_csv}")
    print(f"Tempo total: {metrics.wall_time_seconds:.3f}s")
    print(f"Tempo de CPU: {metrics.cpu_time_seconds:.3f}s")
    if metrics.peak_memory_mb is not None:
        print(f"Pico de memória: {metrics.peak_memory_mb:.3f} MB")
