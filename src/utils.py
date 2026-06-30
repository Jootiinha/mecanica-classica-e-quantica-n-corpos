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
    return build_results_file_path_for_formalism(scenario_file, "newtonian")


def build_formalism_output_dir(formalism: str):
    return Path("outputs") / "formalisms" / formalism


def build_results_file_path_for_formalism(scenario_file: str, formalism: str):
    scenario_stem = Path(scenario_file).stem
    return build_formalism_output_dir(formalism) / "results" / f"{scenario_stem}.npz"


def build_render_output_dir(formalism: str):
    return build_formalism_output_dir(formalism) / "adhoc"


def build_metrics_output_dir(formalism: str):
    return build_formalism_output_dir(formalism)


def build_chart_data_file_path(formalism: str):
    return build_formalism_output_dir(formalism) / "charts" / "execution_metrics_plot_data.tsv"


def build_chart_output_file_path(formalism: str):
    return build_formalism_output_dir(formalism) / "charts" / "execution_metrics.png"
