from pathlib import Path

import yaml


def load_scenarios(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return yaml.safe_load(file)


def _slugify_nome_arquivo(nome):
    nome_normalizado = "".join(
        caractere.lower() if caractere.isalnum() else "_"
        for caractere in nome
    )
    while "__" in nome_normalizado:
        nome_normalizado = nome_normalizado.replace("__", "_")
    return nome_normalizado.strip("_") or "simulacao"


def build_results_file_path(scenario_file: str):
    scenario_stem = Path(scenario_file).stem
    return Path("outputs") / "results" / f"{scenario_stem}.npz"


def build_report_file_path(scenario_file: str):
    scenario_stem = Path(scenario_file).stem
    return Path("outputs") / "reports" / f"{scenario_stem}.md"
