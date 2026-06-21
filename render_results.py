import os

import numpy as np

from src.plot import render_simulation_artifacts
from src.simulacao import FORMALISMS
from src.utils import build_results_file_path, load_scenarios

PATH_SCENARIOS = "./scenarios/"


def _resolve_formalism(results) -> str:
    requested_formalism = (os.environ.get("FORMALISM") or "newtonian").strip().lower()
    if requested_formalism not in FORMALISMS:
        valid = ", ".join(FORMALISMS)
        raise ValueError(f"FORMALISM invalido: {requested_formalism}. Use um de: {valid}")

    formalism_keys = (
        f"{requested_formalism}_time",
        f"{requested_formalism}_r1",
        f"{requested_formalism}_r2",
        f"{requested_formalism}_r_com",
    )
    if all(key in results for key in formalism_keys):
        return requested_formalism

    # Compatibilidade com resultados antigos, que salvavam apenas a serie padrao.
    if {"time", "r1", "r2", "r_com"}.issubset(results.files):
        return "newtonian"

    raise KeyError(
        f"Resultados para o formalismo '{requested_formalism}' nao encontrados no arquivo salvo."
    )


def render_saved_results():
    scenario_file = os.environ.get("SCENARIO")
    if not scenario_file:
        raise ValueError("A variavel de ambiente SCENARIO precisa ser informada.")

    scenario_config = load_scenarios(PATH_SCENARIOS + scenario_file)
    results_path = build_results_file_path(scenario_file)

    if not results_path.exists():
        raise FileNotFoundError(f"Resultados nao encontrados para renderizacao: {results_path}")

    with np.load(results_path) as results:
        formalism = _resolve_formalism(results)
        scenario_for_render = dict(scenario_config)
        scenario_for_render["name"] = f"{scenario_config['name']} [{formalism}]"

        if formalism == "newtonian" and {"time", "r1", "r2", "r_com"}.issubset(results.files):
            time = results["time"]
            r1 = results["r1"]
            r2 = results["r2"]
            r_com = results["r_com"]
        else:
            time = results[f"{formalism}_time"]
            r1 = results[f"{formalism}_r1"]
            r2 = results[f"{formalism}_r2"]
            r_com = results[f"{formalism}_r_com"]

        print(f"Renderizando formalismo: {formalism}")
        render_simulation_artifacts(
            scenario_for_render,
            time,
            r1,
            r2,
            r_com,
        )


if __name__ == "__main__":
    render_saved_results()
