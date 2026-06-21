import os

from src.performance_metrics import ExecutionProfiler, append_metrics_csv
from src.simulacao import simular_dois_corpos_3d
from src.utils import load_scenarios

PATH_SCENARIOS = './scenarios/'


def run_simulation():
    scenario_file = os.environ.get('SCENARIO')
    scenario_config = load_scenarios(PATH_SCENARIOS + scenario_file)

    simular_dois_corpos_3d(scenario_config)


if __name__ == "__main__":
    SAVE_METRICS = False

    os.makedirs("outputs", exist_ok=True)
    run_label = os.environ.get("RUN_LABEL")

    if not SAVE_METRICS:
        run_simulation()
    else:
        profiler = ExecutionProfiler()

        run_simulation()
        
        metrics = profiler.finish(run_label=run_label)
        caminho_csv = append_metrics_csv("outputs", metrics)

        print(f"Métricas salvas em: {caminho_csv}")
        print(f"Tempo total: {metrics.wall_time_seconds:.3f}s")
        print(f"Tempo de CPU: {metrics.cpu_time_seconds:.3f}s")
        if metrics.peak_memory_mb is not None:
            print(f"Pico de memória: {metrics.peak_memory_mb:.3f} MB")
