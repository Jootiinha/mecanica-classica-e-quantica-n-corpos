import os

import numpy as np

from src.performance_metrics import ExecutionProfiler, append_metrics_csv
from src.simulacao import FORMALISMS, simular_dois_corpos_3d
from src.analysis import build_formalism_report, build_trabalho_report
from src.utils import (
    build_comparison_report_file_path,
    build_formalism_report_file_path,
    build_metrics_output_dir,
    build_results_file_path_for_formalism,
    load_scenarios,
)

PATH_SCENARIOS = './scenarios/'


def run_simulation():
    scenario_file = os.environ.get('SCENARIO')
    if not scenario_file:
        raise ValueError("A variavel de ambiente SCENARIO precisa ser informada.")

    scenario_config = load_scenarios(PATH_SCENARIOS + scenario_file)
    run_label = os.environ.get("RUN_LABEL")

    simulation_results = {}
    generated_paths = []

    for formalism in FORMALISMS:
        profiler = ExecutionProfiler()
        result = simular_dois_corpos_3d(scenario_config, formalism=formalism)
        metrics = profiler.finish(run_label=run_label)

        results_path = build_results_file_path_for_formalism(scenario_file, formalism)
        report_path = build_formalism_report_file_path(scenario_file, formalism)
        metrics_output_dir = build_metrics_output_dir(formalism)

        results_path.parent.mkdir(parents=True, exist_ok=True)
        np.savez_compressed(results_path, **result)
        build_formalism_report(scenario_config, formalism, result, report_path)
        csv_path = append_metrics_csv(metrics_output_dir, metrics)

        simulation_results[formalism] = result
        generated_paths.append((formalism, results_path, report_path, csv_path, metrics))

    comparison_report_path = build_comparison_report_file_path(scenario_file)
    build_trabalho_report(scenario_config, simulation_results, comparison_report_path)

    for formalism, results_path, report_path, csv_path, metrics in generated_paths:
        print(f"[{formalism}] Resultados fisicos salvos em: {results_path}")
        print(f"[{formalism}] Relatorio do trabalho salvo em: {report_path}")
        print(f"[{formalism}] Metricas salvas em: {csv_path}")
        print(f"[{formalism}] Tempo total: {metrics.wall_time_seconds:.3f}s")
        print(f"[{formalism}] Tempo de CPU: {metrics.cpu_time_seconds:.3f}s")
        print(f"[{formalism}] CPU medio do processo: {metrics.avg_process_cpu_percent:.2f}%")
        if metrics.avg_machine_cpu_percent is not None:
            print(f"[{formalism}] CPU media da maquina: {metrics.avg_machine_cpu_percent:.2f}%")
        if metrics.peak_memory_mb is not None:
            print(f"[{formalism}] Pico de memoria: {metrics.peak_memory_mb:.3f} MB")

    print(f"[comparison] Relatorio comparativo salvo em: {comparison_report_path}")
    return generated_paths


if __name__ == "__main__":
    os.makedirs("outputs", exist_ok=True)
    run_simulation()
