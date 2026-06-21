import os

import numpy as np

from src.performance_metrics import ExecutionProfiler, append_metrics_csv
from src.trabalho_analysis import build_trabalho_report, run_all_formalisms
from src.utils import build_report_file_path, build_results_file_path, load_scenarios

PATH_SCENARIOS = './scenarios/'


def run_simulation():
    scenario_file = os.environ.get('SCENARIO')
    if not scenario_file:
        raise ValueError("A variavel de ambiente SCENARIO precisa ser informada.")

    scenario_config = load_scenarios(PATH_SCENARIOS + scenario_file)
    simulation_results = run_all_formalisms(scenario_config)
    render_formalism = "newtonian"
    simulation_result = simulation_results[render_formalism]
    results_path = build_results_file_path(scenario_file)
    report_path = build_report_file_path(scenario_file)
    results_path.parent.mkdir(parents=True, exist_ok=True)

    payload = dict(simulation_result)
    payload["render_formalism"] = np.array(render_formalism)
    for formalism, result in simulation_results.items():
        for key, value in result.items():
            payload[f"{formalism}_{key}"] = value

    np.savez_compressed(results_path, **payload)
    build_trabalho_report(scenario_config, simulation_results, report_path)

    print(f"Resultados fisicos salvos em: {results_path}")
    print(f"Relatorio do trabalho salvo em: {report_path}")
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
