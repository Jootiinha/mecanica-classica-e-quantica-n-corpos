from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np

from src.calculos import (
    energial_total,
    hamiltoniano_total,
    momento_angular_total,
    momento_liner_total,
)
from src.simulacao import FORMALISMS, simular_dois_corpos_3d


@dataclass(frozen=True)
class ConservacaoResumo:
    energia_drift_max: float
    momento_linear_drift_max: float
    momento_angular_drift_max: float


def _max_relative_drift(series: np.ndarray) -> float:
    reference = np.linalg.norm(series[0])
    variation = np.linalg.norm(series - series[0], axis=-1) if series.ndim > 1 else np.abs(series - series[0])
    denominator = reference if reference > 1e-12 else 1.0
    return float(np.max(variation) / denominator)


def build_conservation_summary(caso, resultado: dict) -> ConservacaoResumo:
    physics = caso["physics"]

    formalism = str(np.asarray(resultado["formalism"]).item())

    if formalism == "hamiltonian":
        energia = hamiltoniano_total(
            resultado["r1"],
            resultado["r2"],
            resultado["p1"],
            resultado["p2"],
            physics["gravity"],
            resultado["m1_t"],
            resultado["m2_t"],
            physics["eps"],
        )
    else:
        energia = energial_total(
            resultado["r1"],
            resultado["r2"],
            resultado["v1"],
            resultado["v2"],
            physics["gravity"],
            resultado["m1_t"],
            resultado["m2_t"],
            physics["eps"],
        )
    momento_linear = momento_liner_total(
        resultado["v1"],
        resultado["v2"],
        resultado["m1_t"],
        resultado["m2_t"],
    )
    momento_angular = momento_angular_total(
        resultado["r1"],
        resultado["r2"],
        resultado["v1"],
        resultado["v2"],
        resultado["m1_t"],
        resultado["m2_t"],
    )

    return ConservacaoResumo(
        energia_drift_max=_max_relative_drift(energia),
        momento_linear_drift_max=_max_relative_drift(momento_linear),
        momento_angular_drift_max=_max_relative_drift(momento_angular),
    )


def compare_formalisms(resultados: dict[str, dict]) -> dict[str, float]:
    referencia = resultados["newtonian"]
    comparacao = {}

    for formalism in FORMALISMS:
        atual = resultados[formalism]
        if formalism == "newtonian":
            comparacao[f"{formalism}_r1_max_abs_diff_vs_newtonian"] = 0.0
            comparacao[f"{formalism}_r2_max_abs_diff_vs_newtonian"] = 0.0
            continue

        comparacao[f"{formalism}_r1_max_abs_diff_vs_newtonian"] = float(
            np.max(np.abs(atual["r1"] - referencia["r1"]))
        )
        comparacao[f"{formalism}_r2_max_abs_diff_vs_newtonian"] = float(
            np.max(np.abs(atual["r2"] - referencia["r2"]))
        )

    return comparacao


def build_formalism_report(caso, formalism: str, resultado: dict, report_path: Path):
    resumo = build_conservation_summary(caso, resultado)

    lines = [
        f"# Relatorio do Trabalho - {caso['name']} [{formalism}]",
        "",
        "## Formalismo",
        "",
        f"- `{formalism}`",
        "",
        "## Leis de conservacao",
        "",
        f"- `energia_drift_max`: `{resumo.energia_drift_max:.6e}`",
        f"- `momento_linear_drift_max`: `{resumo.momento_linear_drift_max:.6e}`",
        f"- `momento_angular_drift_max`: `{resumo.momento_angular_drift_max:.6e}`",
    ]

    if caso["physics"]["massa_variavel"]:
        lines.extend(
            [
                "",
                "## Observacao sobre massa variavel",
                "",
                "Como as massas dependem explicitamente do tempo, os valores acima servem como diagnostico numerico do sistema modelado, e nao como garantia de conservacao estrita das grandezas classicas.",
            ]
        )

    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def build_trabalho_report(caso, resultados: dict[str, dict], report_path: Path):
    conservation = {
        formalism: build_conservation_summary(caso, resultado)
        for formalism, resultado in resultados.items()
    }
    comparison = compare_formalisms(resultados)

    lines = [
        f"# Relatorio Comparativo do Trabalho - {caso['name']}",
        "",
        "## Formalismos executados",
        "",
    ]
    lines.extend([f"- `{formalism}`" for formalism in FORMALISMS])
    lines.extend(
        [
            "",
            "## Comparacao entre formalismos",
            "",
            "A referencia numerica usada para comparacao foi o formalismo newtoniano.",
            "",
        ]
    )
    for metric_name, metric_value in comparison.items():
        lines.append(f"- `{metric_name}`: `{metric_value:.6e}`")

    lines.extend(
        [
            "",
            "## Leis de conservacao",
            "",
        ]
    )
    for formalism, resumo in conservation.items():
        lines.extend(
            [
                f"### {formalism}",
                "",
                f"- `energia_drift_max`: `{resumo.energia_drift_max:.6e}`",
                f"- `momento_linear_drift_max`: `{resumo.momento_linear_drift_max:.6e}`",
                f"- `momento_angular_drift_max`: `{resumo.momento_angular_drift_max:.6e}`",
                "",
            ]
        )

    if caso["physics"]["massa_variavel"]:
        lines.extend(
            [
                "## Observacao sobre massa variavel",
                "",
                "Como as massas dependem explicitamente do tempo, os valores acima servem como diagnostico numerico do sistema modelado, e nao como garantia de conservacao estrita das grandezas classicas.",
                "",
            ]
        )

    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def run_all_formalisms(caso):
    return {
        formalism: simular_dois_corpos_3d(caso, formalism=formalism)
        for formalism in FORMALISMS
    }
