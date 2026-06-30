import os

import numpy as np

from src.plot import render_simulation_artifacts
from src.utils import build_results_file_path_for_formalism, load_scenarios

PATH_SCENARIOS = "./scenarios/"
FORMALISM = "newtonian"

def _resolve_formalism() -> str:
    requested_formalism = (os.environ.get("FORMALISM") or FORMALISM).strip().lower()
    if requested_formalism != FORMALISM:
        raise ValueError(f"FORMALISM invalido: {requested_formalism}. Use apenas: {FORMALISM}")
    return requested_formalism


def render_saved_results():
    scenario_file = os.environ.get("SCENARIO")
    if not scenario_file:
        raise ValueError("A variavel de ambiente SCENARIO precisa ser informada.")

    scenario_config = load_scenarios(PATH_SCENARIOS + scenario_file)
    formalism = _resolve_formalism()
    results_path = build_results_file_path_for_formalism(scenario_file, formalism)

    if not results_path.exists():
        raise FileNotFoundError(f"Resultados nao encontrados para renderizacao: {results_path}")

    with np.load(results_path) as results:
        scenario_for_render = dict(scenario_config)
        scenario_for_render["name"] = f"{scenario_config['name']} [{formalism}]"
        print(f"Renderizando formalismo: {formalism}")
        render_simulation_artifacts(
            scenario_for_render,
            results["time"],
            results["r1"],
            results["r2"],
            results["r_com"],
            formalism=formalism,
        )


if __name__ == "__main__":
    render_saved_results()
