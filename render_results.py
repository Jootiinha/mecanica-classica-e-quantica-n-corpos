import os

import numpy as np

from src.plot import render_simulation_artifacts
from src.utils import build_results_file_path, load_scenarios

PATH_SCENARIOS = "./scenarios/"


def render_saved_results():
    scenario_file = os.environ.get("SCENARIO")
    if not scenario_file:
        raise ValueError("A variavel de ambiente SCENARIO precisa ser informada.")

    scenario_config = load_scenarios(PATH_SCENARIOS + scenario_file)
    results_path = build_results_file_path(scenario_file)

    if not results_path.exists():
        raise FileNotFoundError(f"Resultados nao encontrados para renderizacao: {results_path}")

    with np.load(results_path) as results:
        render_simulation_artifacts(
            scenario_config,
            results["time"],
            results["r1"],
            results["r2"],
            results["r_com"],
        )


if __name__ == "__main__":
    render_saved_results()
