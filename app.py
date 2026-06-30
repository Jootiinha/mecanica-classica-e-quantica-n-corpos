from __future__ import annotations

import copy
import json
import time
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import plotly.graph_objects as go
import streamlit as st

from src.calculos import energial_total, momento_angular_total, momento_liner_total
from src.simulacao import INTEGRATION_METHODS, simular_dois_corpos_3d
from src.utils import build_formalism_output_dir, load_scenarios

SCENARIOS_DIR = Path("scenarios")
FORMALISM = "newtonian"
FORMALISM_LABEL = "newtoniano"
STREAMLIT_RUNS_DIR = build_formalism_output_dir(FORMALISM) / "streamlit_runs"
STREAMLIT_RUNS_INDEX_PATH = STREAMLIT_RUNS_DIR / "index.json"


@st.cache_data(show_spinner=False)
def list_scenarios() -> list[str]:
    return sorted(path.name for path in SCENARIOS_DIR.glob("*.yaml"))


@st.cache_data(show_spinner=False)
def load_scenario_config(scenario_name: str) -> dict:
    return load_scenarios(str(SCENARIOS_DIR / scenario_name))


@st.cache_data(show_spinner=False)
def run_simulation_cached(
    config_json: str,
    integration_method: str,
    rtol: float,
    atol: float,
) -> tuple[dict, float]:
    scenario_config = json.loads(config_json)
    start = time.perf_counter()
    result = simular_dois_corpos_3d(
        scenario_config,
        formalism=FORMALISM,
        integration_method=integration_method,
        rtol=rtol,
        atol=atol,
    )
    elapsed = time.perf_counter() - start
    return result, elapsed


def vector_input(label: str, values: list[float], step: float = 0.1) -> list[float]:
    cols = st.columns(3)
    axes = ("x", "y", "z")
    updated_values = []
    for index, axis in enumerate(axes):
        updated_values.append(
            cols[index].number_input(
                f"{label} {axis}",
                value=float(values[index]),
                step=step,
                format="%.6f",
            )
        )
    return updated_values


def _vector_norm(values: list[float]) -> float:
    return float(np.linalg.norm(np.asarray(values, dtype=float)))


def step_for_value(value: float, minimum: float = 1e-6) -> float:
    return max(abs(float(value)) * 0.1, minimum)


def _axis_ranges(result: dict) -> dict[str, list[float]]:
    points = np.vstack((result["r1"], result["r2"], result["r_com"]))
    mins = points.min(axis=0)
    maxs = points.max(axis=0)
    center = 0.5 * (mins + maxs)
    spans = np.maximum(maxs - mins, 1.0)
    radius = 0.6 * float(spans.max())
    return {
        "x": [float(center[0] - radius), float(center[0] + radius)],
        "y": [float(center[1] - radius), float(center[1] + radius)],
        "z": [float(center[2] - radius), float(center[2] + radius)],
    }


def _axis_ranges_for_runs(runs: list[dict]) -> dict[str, list[float]]:
    points = np.vstack(
        [
            np.vstack((run["result"]["r1"], run["result"]["r2"], run["result"]["r_com"]))
            for run in runs
        ]
    )
    mins = points.min(axis=0)
    maxs = points.max(axis=0)
    center = 0.5 * (mins + maxs)
    spans = np.maximum(maxs - mins, 1.0)
    radius = 0.6 * float(spans.max())
    return {
        "x": [float(center[0] - radius), float(center[0] + radius)],
        "y": [float(center[1] - radius), float(center[1] + radius)],
        "z": [float(center[2] - radius), float(center[2] + radius)],
    }


def _max_relative_drift(series: np.ndarray) -> float:
    reference = np.linalg.norm(series[0]) if series.ndim > 1 else abs(float(series[0]))
    variation = np.linalg.norm(series - series[0], axis=-1) if series.ndim > 1 else np.abs(series - series[0])
    denominator = reference if reference > 1e-12 else 1.0
    return float(np.max(variation) / denominator)


def _distance_series(result: dict) -> np.ndarray:
    return np.linalg.norm(result["r2"] - result["r1"], axis=1)


def _compute_analysis_series(config: dict, result: dict) -> dict[str, np.ndarray | float]:
    physics = config["physics"]
    energy_series = energial_total(
        result["r1"],
        result["r2"],
        result["v1"],
        result["v2"],
        physics["gravity"],
        result["m1_t"],
        result["m2_t"],
        physics["eps"],
    )
    linear_momentum = momento_liner_total(
        result["v1"],
        result["v2"],
        result["m1_t"],
        result["m2_t"],
    )
    angular_momentum = momento_angular_total(
        result["r1"],
        result["r2"],
        result["v1"],
        result["v2"],
        result["m1_t"],
        result["m2_t"],
    )

    return {
        "distance_series": _distance_series(result),
        "energy_series": energy_series,
        "linear_momentum_norm": np.linalg.norm(linear_momentum, axis=1),
        "angular_momentum_norm": np.linalg.norm(angular_momentum, axis=1),
        "energy_drift_max": _max_relative_drift(energy_series),
        "linear_momentum_drift_max": _max_relative_drift(linear_momentum),
        "angular_momentum_drift_max": _max_relative_drift(angular_momentum),
    }


def _build_run_label(config: dict, integration_method: str, run_index: int) -> str:
    scenario_name = config["name"]
    return f"{run_index:02d} | {scenario_name} | {integration_method}"


def _run_npz_path(run_id: int) -> Path:
    return STREAMLIT_RUNS_DIR / f"run_{run_id:04d}.npz"


def _ensure_streamlit_runs_dir() -> None:
    STREAMLIT_RUNS_DIR.mkdir(parents=True, exist_ok=True)


def _run_result_payload(result: dict, analysis: dict) -> dict[str, np.ndarray]:
    payload = {
        "time": result["time"],
        "r1": result["r1"],
        "r2": result["r2"],
        "v1": result["v1"],
        "v2": result["v2"],
        "p1": result["p1"],
        "p2": result["p2"],
        "r_com": result["r_com"],
        "m1_t": result["m1_t"],
        "m2_t": result["m2_t"],
        "distance_series": analysis["distance_series"],
        "energy_series": analysis["energy_series"],
        "linear_momentum_norm": analysis["linear_momentum_norm"],
        "angular_momentum_norm": analysis["angular_momentum_norm"],
    }
    return payload


def _persist_run_record(run_record: dict) -> None:
    _ensure_streamlit_runs_dir()
    np.savez_compressed(_run_npz_path(run_record["id"]), **_run_result_payload(run_record["result"], run_record["analysis"]))

    current_index = []
    if STREAMLIT_RUNS_INDEX_PATH.exists():
        current_index = json.loads(STREAMLIT_RUNS_INDEX_PATH.read_text(encoding="utf-8"))

    current_index = [entry for entry in current_index if entry["id"] != run_record["id"]]
    current_index.append(
        {
            "id": run_record["id"],
            "label": run_record["label"],
            "scenario_name": run_record["scenario_name"],
            "integration_method": run_record["integration_method"],
            "rtol": run_record["rtol"],
            "atol": run_record["atol"],
            "elapsed": run_record["elapsed"],
            "n_points": run_record["n_points"],
            "nfev": run_record["nfev"],
            "distance_final": run_record["distance_final"],
            "distance_min": run_record["distance_min"],
            "energy_drift_max": run_record["energy_drift_max"],
            "linear_momentum_drift_max": run_record["linear_momentum_drift_max"],
            "angular_momentum_drift_max": run_record["angular_momentum_drift_max"],
            "created_at": run_record["created_at"],
            "config": run_record["config"],
        }
    )
    current_index.sort(key=lambda entry: entry["id"])
    STREAMLIT_RUNS_INDEX_PATH.write_text(
        json.dumps(current_index, ensure_ascii=True, indent=2),
        encoding="utf-8",
    )


def _load_persisted_runs() -> list[dict]:
    if not STREAMLIT_RUNS_INDEX_PATH.exists():
        return []

    raw_index = json.loads(STREAMLIT_RUNS_INDEX_PATH.read_text(encoding="utf-8"))
    runs = []
    for entry in raw_index:
        npz_path = _run_npz_path(entry["id"])
        if not npz_path.exists():
            continue

        with np.load(npz_path) as data:
            result = {
                "time": data["time"],
                "r1": data["r1"],
                "r2": data["r2"],
                "v1": data["v1"],
                "v2": data["v2"],
                "p1": data["p1"],
                "p2": data["p2"],
                "r_com": data["r_com"],
                "m1_t": data["m1_t"],
                "m2_t": data["m2_t"],
                "formalism": FORMALISM,
                "integration_method": entry["integration_method"],
                "rtol": float(entry["rtol"]),
                "atol": float(entry["atol"]),
                "nfev": int(entry["nfev"]),
            }
            analysis = {
                "distance_series": data["distance_series"],
                "energy_series": data["energy_series"],
                "linear_momentum_norm": data["linear_momentum_norm"],
                "angular_momentum_norm": data["angular_momentum_norm"],
            }

        runs.append(
            {
                "id": int(entry["id"]),
                "label": entry["label"],
                "scenario_name": entry["scenario_name"],
                "integration_method": entry["integration_method"],
                "rtol": float(entry["rtol"]),
                "atol": float(entry["atol"]),
                "elapsed": float(entry["elapsed"]),
                "n_points": int(entry["n_points"]),
                "nfev": int(entry["nfev"]),
                "distance_final": float(entry["distance_final"]),
                "distance_min": float(entry["distance_min"]),
                "energy_drift_max": float(entry["energy_drift_max"]),
                "linear_momentum_drift_max": float(entry["linear_momentum_drift_max"]),
                "angular_momentum_drift_max": float(entry["angular_momentum_drift_max"]),
                "created_at": entry["created_at"],
                "config": entry["config"],
                "result": result,
                "analysis": analysis,
            }
        )

    runs.sort(key=lambda run: run["id"])
    return runs


def _clear_persisted_runs() -> None:
    if STREAMLIT_RUNS_DIR.exists():
        for path in STREAMLIT_RUNS_DIR.glob("run_*.npz"):
            path.unlink(missing_ok=True)
    STREAMLIT_RUNS_INDEX_PATH.unlink(missing_ok=True)


def build_runs_table_rows(runs: list[dict]) -> list[dict[str, str | int | float]]:
    rows = []
    for run in runs:
        rows.append(
            {
                "Rodada": f"{run['id']:02d}",
                "Cenario": run["scenario_name"],
                "Metodo": run["integration_method"],
                "rtol": f"{run['rtol']:.1e}",
                "atol": f"{run['atol']:.1e}",
                "Tempo de calculo (s)": f"{run['elapsed']:.3f}",
                "Amostras da trajetoria": run["n_points"],
                "Avaliacoes da EDO": run["nfev"],
                "Erro relativo energia": f"{run['energy_drift_max']:.3e}",
                "Erro relativo momento angular": f"{run['angular_momentum_drift_max']:.3e}",
            }
        )
    return rows


def _run_chart_ref(run: dict) -> str:
    return f"R{run['id']:02d}"


def _run_chart_name(run: dict) -> str:
    return f"{_run_chart_ref(run)} · {run['integration_method']}"


def build_series_comparison_chart(
    runs: list[dict],
    series_key: str,
    title: str,
    yaxis_title: str,
) -> go.Figure:
    fig = go.Figure()
    for run in runs:
        customdata = np.column_stack(
            [
                np.full(len(run["result"]["time"]), _run_chart_ref(run), dtype=object),
                np.full(len(run["result"]["time"]), run["scenario_name"], dtype=object),
                np.full(len(run["result"]["time"]), run["integration_method"], dtype=object),
            ]
        )
        fig.add_trace(
            go.Scatter(
                x=run["result"]["time"],
                y=run["analysis"][series_key],
                mode="lines",
                name=_run_chart_name(run),
                customdata=customdata,
                hovertemplate=(
                    "Rodada: %{customdata[0]}<br>"
                    "Cenário: %{customdata[1]}<br>"
                    "Método: %{customdata[2]}<br>"
                    "tempo: %{x:.3f}<br>"
                    "valor: %{y:.6g}<extra></extra>"
                ),
            )
        )

    fig.update_layout(
        title=dict(text=title, x=0.0, xanchor="left"),
        xaxis_title="tempo",
        yaxis_title=yaxis_title,
        height=420,
        margin=dict(l=0, r=0, t=72, b=96),
        legend=dict(orientation="h", yanchor="top", y=-0.22, xanchor="left", x=0.0),
    )
    return fig


def build_runtime_comparison_chart(runs: list[dict]) -> go.Figure:
    labels = [_run_chart_ref(run) for run in runs]
    elapsed = [run["elapsed"] for run in runs]
    nfev = [run["nfev"] for run in runs]
    scenario_names = [run["scenario_name"] for run in runs]
    methods = [run["integration_method"] for run in runs]

    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            name="Tempo de cálculo (s)",
            x=labels,
            y=elapsed,
            customdata=np.column_stack([scenario_names, methods]),
            hovertemplate=(
                "Rodada: %{x}<br>"
                "Cenário: %{customdata[0]}<br>"
                "Método: %{customdata[1]}<br>"
                "tempo: %{y:.3f}s<extra></extra>"
            ),
        )
    )
    fig.add_trace(
        go.Bar(
            name="Avaliações da EDO",
            x=labels,
            y=nfev,
            yaxis="y2",
            customdata=np.column_stack([scenario_names, methods]),
            hovertemplate=(
                "Rodada: %{x}<br>"
                "Cenário: %{customdata[0]}<br>"
                "Método: %{customdata[1]}<br>"
                "avaliações: %{y}<extra></extra>"
            ),
        )
    )

    fig.update_layout(
        title=dict(text="Comparação de custo numérico", x=0.0, xanchor="left"),
        height=420,
        margin=dict(l=0, r=0, t=72, b=96),
        barmode="group",
        yaxis=dict(title="tempo (s)"),
        yaxis2=dict(title="avaliações", overlaying="y", side="right"),
        xaxis=dict(title="rodada", tickangle=-20),
        legend=dict(orientation="h", yanchor="top", y=-0.22, xanchor="left", x=0.0),
    )
    return fig


def build_trajectory_comparison_chart(runs: list[dict]) -> go.Figure:
    fig = go.Figure()
    axis_ranges = _axis_ranges_for_runs(runs)
    palette = [
        "#123c69",
        "#d1495b",
        "#2a9d8f",
        "#6c584c",
        "#8f5bd6",
        "#ef476f",
        "#118ab2",
        "#f4a261",
    ]

    for index, run in enumerate(runs):
        color = palette[index % len(palette)]
        customdata = np.column_stack(
            [
                np.full(len(run["result"]["time"]), _run_chart_ref(run), dtype=object),
                np.full(len(run["result"]["time"]), run["scenario_name"], dtype=object),
                np.full(len(run["result"]["time"]), run["integration_method"], dtype=object),
            ]
        )
        common_trace = dict(
            mode="lines",
            customdata=customdata,
            hovertemplate=(
                "Rodada: %{customdata[0]}<br>"
                "Cenário: %{customdata[1]}<br>"
                "Método: %{customdata[2]}<br>"
                "x: %{x:.6g}<br>"
                "y: %{y:.6g}<br>"
                "z: %{z:.6g}<extra></extra>"
            ),
        )
        fig.add_trace(
            go.Scatter3d(
                x=run["result"]["r1"][:, 0],
                y=run["result"]["r1"][:, 1],
                z=run["result"]["r1"][:, 2],
                name=f"{_run_chart_name(run)} · corpo 1",
                line=dict(color=color, width=6),
                legendgroup=_run_chart_ref(run),
                **common_trace,
            )
        )
        fig.add_trace(
            go.Scatter3d(
                x=run["result"]["r2"][:, 0],
                y=run["result"]["r2"][:, 1],
                z=run["result"]["r2"][:, 2],
                name=f"{_run_chart_name(run)} · corpo 2",
                line=dict(color=color, width=4, dash="dash"),
                legendgroup=_run_chart_ref(run),
                **common_trace,
            )
        )

    fig.update_layout(
        title=dict(text="Trajetórias 3D sobrepostas", x=0.0, xanchor="left"),
        height=720,
        margin=dict(l=0, r=0, t=72, b=0),
        legend=dict(orientation="h", yanchor="top", y=-0.12, xanchor="left", x=0.0),
        scene=dict(
            xaxis_title="x",
            yaxis_title="y",
            zaxis_title="z",
            xaxis=dict(range=axis_ranges["x"]),
            yaxis=dict(range=axis_ranges["y"]),
            zaxis=dict(range=axis_ranges["z"]),
            aspectmode="cube",
            camera=dict(eye=dict(x=1.55, y=1.4, z=0.9)),
        ),
    )
    return fig


def build_drift_summary_chart(runs: list[dict]) -> go.Figure:
    labels = [_run_chart_ref(run) for run in runs]
    energy = [run["energy_drift_max"] for run in runs]
    angular = [run["angular_momentum_drift_max"] for run in runs]
    linear = [run["linear_momentum_drift_max"] for run in runs]
    scenario_names = [run["scenario_name"] for run in runs]
    methods = [run["integration_method"] for run in runs]

    fig = go.Figure()
    fig.add_trace(go.Bar(name="Energia", x=labels, y=energy, customdata=np.column_stack([scenario_names, methods])))
    fig.add_trace(go.Bar(name="Momento angular", x=labels, y=angular, customdata=np.column_stack([scenario_names, methods])))
    fig.add_trace(go.Bar(name="Momento linear", x=labels, y=linear, customdata=np.column_stack([scenario_names, methods])))

    fig.update_layout(
        title=dict(text="Resumo de erro relativo máximo", x=0.0, xanchor="left"),
        height=420,
        margin=dict(l=0, r=0, t=72, b=96),
        barmode="group",
        yaxis=dict(title="erro relativo máximo"),
        xaxis=dict(title="rodada", tickangle=-20),
        legend=dict(orientation="h", yanchor="top", y=-0.22, xanchor="left", x=0.0),
    )
    fig.update_traces(
        hovertemplate=(
            "Rodada: %{x}<br>"
            "Cenário: %{customdata[0]}<br>"
            "Método: %{customdata[1]}<br>"
            "valor: %{y:.6g}<extra></extra>"
        )
    )
    return fig


def build_animated_plot(
    result: dict,
    scenario_name: str,
    stride: int,
    playback_ms: int,
) -> go.Figure:
    r1 = result["r1"][::stride]
    r2 = result["r2"][::stride]
    r_com = result["r_com"][::stride]
    time_points = result["time"][::stride]
    axis_ranges = _axis_ranges(result)
    total_frames = len(time_points)
    integration_method = str(result["integration_method"])

    def marker_trace(index: int) -> go.Scatter3d:
        return go.Scatter3d(
            x=[r1[index, 0], r2[index, 0], r_com[index, 0]],
            y=[r1[index, 1], r2[index, 1], r_com[index, 1]],
            z=[r1[index, 2], r2[index, 2], r_com[index, 2]],
            mode="markers",
            name="Posição atual",
            marker=dict(
                size=[8, 8, 6],
                color=["#123c69", "#d1495b", "#ffffff"],
                line=dict(color="#111111", width=1),
            ),
        )

    fig = go.Figure(
        data=[
            go.Scatter3d(x=r1[:1, 0], y=r1[:1, 1], z=r1[:1, 2], mode="lines", name="Corpo 1", line=dict(color="#123c69", width=6)),
            go.Scatter3d(x=r2[:1, 0], y=r2[:1, 1], z=r2[:1, 2], mode="lines", name="Corpo 2", line=dict(color="#d1495b", width=6)),
            go.Scatter3d(x=r_com[:1, 0], y=r_com[:1, 1], z=r_com[:1, 2], mode="lines", name="Centro de massa", line=dict(color="#ffffff", width=4, dash="dash")),
            marker_trace(0),
        ],
        frames=[
            go.Frame(
                name=str(index),
                data=[
                    go.Scatter3d(x=r1[: index + 1, 0], y=r1[: index + 1, 1], z=r1[: index + 1, 2], mode="lines", line=dict(color="#123c69", width=6)),
                    go.Scatter3d(x=r2[: index + 1, 0], y=r2[: index + 1, 1], z=r2[: index + 1, 2], mode="lines", line=dict(color="#d1495b", width=6)),
                    go.Scatter3d(x=r_com[: index + 1, 0], y=r_com[: index + 1, 1], z=r_com[: index + 1, 2], mode="lines", line=dict(color="#ffffff", width=4, dash="dash")),
                    marker_trace(index),
                ],
                layout=go.Layout(
                    annotations=[
                        dict(
                            x=0.99,
                            y=0.99,
                            xref="paper",
                            yref="paper",
                            text=f"t = {float(time_points[index]):.3f}",
                            showarrow=False,
                            bgcolor="rgba(255,255,255,0.88)",
                        )
                    ]
                ),
            )
            for index in range(total_frames)
        ],
    )

    fig.update_layout(
        title=dict(
            text=f"{scenario_name} [{FORMALISM_LABEL} | {integration_method}]",
            x=0.0,
            xanchor="left",
            y=0.98,
            yanchor="top",
        ),
        height=820,
        margin=dict(l=0, r=0, t=104, b=0),
        legend=dict(orientation="h", yanchor="bottom", y=0.02, xanchor="left", x=0.02, bgcolor="rgba(255,255,255,0.72)"),
        scene=dict(
            xaxis_title="x",
            yaxis_title="y",
            zaxis_title="z",
            xaxis=dict(range=axis_ranges["x"]),
            yaxis=dict(range=axis_ranges["y"]),
            zaxis=dict(range=axis_ranges["z"]),
            aspectmode="cube",
            camera=dict(eye=dict(x=1.55, y=1.4, z=0.9)),
        ),
        annotations=[
            dict(
                x=0.99,
                y=0.99,
                xref="paper",
                yref="paper",
                text=f"t = {float(time_points[0]):.3f}",
                showarrow=False,
                bgcolor="rgba(255,255,255,0.88)",
            )
        ],
        updatemenus=[
            dict(
                type="buttons",
                direction="left",
                x=0.0,
                y=1.02,
                showactive=False,
                buttons=[
                    dict(label="Play", method="animate", args=[None, {"frame": {"duration": playback_ms, "redraw": True}, "transition": {"duration": 0}, "fromcurrent": True}]),
                    dict(label="Pause", method="animate", args=[[None], {"frame": {"duration": 0, "redraw": True}, "transition": {"duration": 0}, "mode": "immediate"}]),
                ],
            )
        ],
        sliders=[
            dict(
                active=0,
                x=0.08,
                y=0.0,
                len=0.88,
                currentvalue={"prefix": "Frame: "},
                steps=[
                    {
                        "label": str(index),
                        "method": "animate",
                        "args": [[str(index)], {"frame": {"duration": 0, "redraw": True}, "transition": {"duration": 0}, "mode": "immediate"}],
                    }
                    for index in range(total_frames)
                ],
            )
        ],
    )
    return fig


def _render_config_overview(config: dict, integration_method: str, rtol: float, atol: float) -> None:
    physics = config["physics"]
    summary_cols = st.columns(6)
    summary_cols[0].metric("Integrador", integration_method)
    summary_cols[1].metric("Tempo final", f"{float(physics['t_final']):.3f}")
    summary_cols[2].metric("Pontos", int(physics["n_pontos"]))
    summary_cols[3].metric("Massa variável", "Sim" if physics["massa_variavel"] else "Não")
    summary_cols[4].metric("||v_cm||", f"{_vector_norm(physics['center_mass_velocity']):.3f}")
    summary_cols[5].metric("rtol / atol", f"{rtol:.0e} / {atol:.0e}")


def _build_run_record(
    config: dict,
    result: dict,
    elapsed: float,
    integration_method: str,
    rtol: float,
    atol: float,
    run_index: int,
) -> dict:
    analysis = _compute_analysis_series(config, result)
    created_at = datetime.now(timezone.utc).isoformat()
    return {
        "id": run_index,
        "label": _build_run_label(config, integration_method, run_index),
        "scenario_name": config["name"],
        "integration_method": integration_method,
        "rtol": float(rtol),
        "atol": float(atol),
        "elapsed": float(elapsed),
        "n_points": int(len(result["time"])),
        "nfev": int(result["nfev"]),
        "distance_final": float(analysis["distance_series"][-1]),
        "distance_min": float(analysis["distance_series"].min()),
        "energy_drift_max": float(analysis["energy_drift_max"]),
        "linear_momentum_drift_max": float(analysis["linear_momentum_drift_max"]),
        "angular_momentum_drift_max": float(analysis["angular_momentum_drift_max"]),
        "created_at": created_at,
        "config": copy.deepcopy(config),
        "result": result,
        "analysis": analysis,
    }


def main() -> None:
    st.set_page_config(page_title="Simulação gravitacional animada", layout="wide")

    if "runs_loaded_from_disk" not in st.session_state:
        persisted_runs = _load_persisted_runs()
        st.session_state.simulation_runs = persisted_runs
        st.session_state.run_counter = max((run["id"] for run in persisted_runs), default=0)
        st.session_state.active_run_id = persisted_runs[-1]["id"] if persisted_runs else None
        st.session_state.runs_loaded_from_disk = True
    elif "simulation_runs" not in st.session_state:
        st.session_state.simulation_runs = []

    st.title("Simulação gravitacional animada")
    st.caption(
        "Edite a configuração em blocos, execute a simulação e compare rodadas por integrador, "
        "tolerâncias e parâmetros físicos. As rodadas ficam salvas em arquivo."
    )

    scenario_names = list_scenarios()
    if not scenario_names:
        st.error("Nenhum arquivo YAML foi encontrado em ./scenarios.")
        return

    st.sidebar.header("Cenário base")
    selected_scenario = st.sidebar.selectbox("Cenário base", scenario_names)
    default_config = copy.deepcopy(load_scenario_config(selected_scenario))
    physics = default_config["physics"]

    st.sidebar.header("Visualização")
    preview_points = st.sidebar.slider("Máximo de frames na animação", 60, 300, 180, step=20)
    playback_ms = st.sidebar.slider("Velocidade da animação (ms/frame)", 25, 250, 60, step=5)
    st.sidebar.caption(f"Formalismo fixo: {FORMALISM_LABEL}")

    st.subheader("Configuração da simulação")
    st.caption("Os campos foram agrupados por responsabilidade para separar solver, parâmetros físicos e estado inicial.")

    with st.form("simulation_configuration"):
        execution_cols = st.columns([1.15, 1.05, 0.9, 0.9])
        integration_method = execution_cols[0].selectbox("Integrador", INTEGRATION_METHODS, index=0)
        physics["t_final"] = execution_cols[1].number_input(
            "Tempo final",
            value=float(physics["t_final"]),
            min_value=0.1,
            step=1.0,
            format="%.3f",
        )
        rtol = execution_cols[2].number_input("Tolerância relativa (rtol)", value=1e-10, min_value=1e-14, format="%.1e")
        atol = execution_cols[3].number_input("Tolerância absoluta (atol)", value=1e-10, min_value=1e-14, format="%.1e")

        st.markdown("**Parâmetros físicos**")
        physical_cols = st.columns(4)
        physics["gravity"] = physical_cols[0].number_input(
            "Constante gravitacional",
            value=float(physics["gravity"]),
            step=step_for_value(physics["gravity"], 0.01),
            format="%.6f",
        )
        physics["eps"] = physical_cols[1].number_input(
            "Amortecimento eps",
            value=float(physics["eps"]),
            min_value=0.0,
            step=step_for_value(physics["eps"], 0.001),
            format="%.6f",
        )
        physics["m1"] = physical_cols[2].number_input(
            "Massa do corpo 1",
            value=float(physics["m1"]),
            min_value=1e-9,
            step=step_for_value(physics["m1"]),
            format="%.6f",
        )
        physics["m2"] = physical_cols[3].number_input(
            "Massa do corpo 2",
            value=float(physics["m2"]),
            min_value=1e-9,
            step=step_for_value(physics["m2"]),
            format="%.6f",
        )

        numerical_cols = st.columns([1.2, 1.0, 1.0, 1.0])
        physics["n_pontos"] = int(
            numerical_cols[0].slider(
                "Quantidade de pontos",
                min_value=200,
                max_value=12000,
                value=int(physics["n_pontos"]),
                step=100,
            )
        )
        physics["massa_variavel"] = numerical_cols[1].checkbox("Massa variável", value=bool(physics["massa_variavel"]))
        if physics["massa_variavel"]:
            physics["tau1"] = numerical_cols[2].number_input(
                "Tau 1",
                value=float(physics["tau1"] or 1.0),
                min_value=0.001,
                step=1.0,
                format="%.6f",
            )
            physics["tau2"] = numerical_cols[3].number_input(
                "Tau 2",
                value=float(physics["tau2"] or 1.0),
                min_value=0.001,
                step=1.0,
                format="%.6f",
            )
        else:
            physics["tau1"] = None
            physics["tau2"] = None
            numerical_cols[2].caption("Tau 1 desabilitado")
            numerical_cols[3].caption("Tau 2 desabilitado")

        st.markdown("**Condições iniciais**")
        body_cols = st.columns(2)
        with body_cols[0]:
            st.caption("Corpo 1")
            physics["initial_position_body_1"] = vector_input("Posição inicial corpo 1", physics["initial_position_body_1"])
            physics["initial_velocity_body_1"] = vector_input("Velocidade inicial corpo 1", physics["initial_velocity_body_1"])
        with body_cols[1]:
            st.caption("Corpo 2")
            physics["initial_position_body_2"] = vector_input("Posição inicial corpo 2", physics["initial_position_body_2"])
            physics["initial_velocity_body_2"] = vector_input("Velocidade inicial corpo 2", physics["initial_velocity_body_2"])

        st.caption("Centro de massa")
        physics["center_mass_velocity"] = vector_input("Velocidade do centro de massa", physics["center_mass_velocity"])

        st.markdown("**Resumo antes da execução**")
        _render_config_overview(default_config, integration_method, rtol, atol)

        action_cols = st.columns([1, 1, 4])
        simulate_clicked = action_cols[0].form_submit_button("Simular", type="primary", use_container_width=True)

    clear_cols = st.columns([1, 1, 4])
    clear_clicked = clear_cols[0].button("Limpar comparações", use_container_width=True)

    if clear_clicked:
        st.session_state.simulation_runs = []
        st.session_state.active_run_id = None
        st.session_state.run_counter = 0
        _clear_persisted_runs()
        st.rerun()

    if simulate_clicked:
        config_json = json.dumps(default_config, sort_keys=True)
        try:
            with st.spinner("Executando a simulação..."):
                result, elapsed = run_simulation_cached(config_json, integration_method, rtol, atol)
        except Exception as exc:
            st.error(f"Falha ao executar a simulação: {exc}")
            return

        st.session_state.run_counter += 1
        run_record = _build_run_record(default_config, result, elapsed, integration_method, rtol, atol, st.session_state.run_counter)
        st.session_state.simulation_runs.append(run_record)
        st.session_state.active_run_id = run_record["id"]
        _persist_run_record(run_record)
        st.success(f"Rodada registrada e salva em arquivo: {run_record['label']}")

    runs = st.session_state.simulation_runs
    if not runs:
        st.info("Nenhuma rodada executada ainda. Ajuste os parâmetros e clique em Simular.")
        return

    st.sidebar.header("Rodadas")
    run_labels = [run["label"] for run in runs]
    active_index = next((index for index, run in enumerate(runs) if run["id"] == st.session_state.active_run_id), len(runs) - 1)
    selected_label = st.sidebar.selectbox("Rodada exibida na animação", run_labels, index=active_index)
    active_run = next(run for run in runs if run["label"] == selected_label)
    st.session_state.active_run_id = active_run["id"]

    total_points = len(active_run["result"]["time"])
    stride = max(1, total_points // preview_points)
    animated_points = len(active_run["result"]["time"][::stride])

    animation_tab, comparison_tab, details_tab = st.tabs(["Animação", "Comparações", "Detalhes"])

    with animation_tab:
        metrics = st.columns(6)
        metrics[0].metric("Tempo de cálculo", f"{active_run['elapsed']:.3f}s")
        metrics[1].metric("Integrador", active_run["integration_method"])
        metrics[2].metric("Pontos integrados", active_run["n_points"])
        metrics[3].metric("Frames exibidos", animated_points)
        metrics[4].metric("Avaliações da EDO", active_run["nfev"])
        metrics[5].metric("Erro rel. máx. energia", f"{active_run['energy_drift_max']:.3e}")

        st.caption(
            "A animação mostra a rodada selecionada na barra lateral. Use os controles laterais "
            "para ajustar densidade de frames e velocidade de playback."
        )
        st.plotly_chart(
            build_animated_plot(active_run["result"], active_run["scenario_name"], stride, playback_ms),
            use_container_width=True,
        )

    with comparison_tab:
        st.subheader("Comparação de rodadas")
        st.caption(
            "Erro relativo de energia e erro relativo de momento angular medem o maior desvio relativo em relação ao valor inicial "
            "da rodada. Em geral, quanto menor esse número, melhor a conservação numérica."
        )

        available_scenarios = sorted({run["scenario_name"] for run in runs})
        available_methods = sorted({run["integration_method"] for run in runs})
        filter_cols = st.columns([1.6, 1.0])
        selected_scenarios = filter_cols[0].multiselect(
            "Cenários incluídos",
            options=available_scenarios,
            default=available_scenarios,
        )
        selected_methods = filter_cols[1].multiselect(
            "Métodos incluídos",
            options=available_methods,
            default=available_methods,
        )

        filtered_runs = [
            run
            for run in runs
            if run["scenario_name"] in selected_scenarios and run["integration_method"] in selected_methods
        ]
        if not filtered_runs:
            st.info("Nenhuma rodada corresponde aos filtros selecionados.")
            return

        fastest_run = min(filtered_runs, key=lambda run: run["elapsed"])
        lowest_energy_drift_run = min(filtered_runs, key=lambda run: run["energy_drift_max"])
        lowest_angular_drift_run = min(filtered_runs, key=lambda run: run["angular_momentum_drift_max"])
        summary_metrics = st.columns(4)
        summary_metrics[0].metric("Rodadas comparadas", len(filtered_runs))
        summary_metrics[1].metric("Mais rápida", _run_chart_name(fastest_run), f"{fastest_run['elapsed']:.3f}s")
        summary_metrics[2].metric("Menor erro rel. de energia", _run_chart_name(lowest_energy_drift_run), f"{lowest_energy_drift_run['energy_drift_max']:.3e}")
        summary_metrics[3].metric("Menor erro rel. de L", _run_chart_name(lowest_angular_drift_run), f"{lowest_angular_drift_run['angular_momentum_drift_max']:.3e}")

        with st.expander("Tabela resumida das rodadas", expanded=True):
            st.dataframe(build_runs_table_rows(filtered_runs), use_container_width=True, hide_index=True)

        st.plotly_chart(build_trajectory_comparison_chart(filtered_runs), use_container_width=True)
        st.caption(
            "Para evidenciar a diferença entre integradores, filtre um único cenário e mantenha apenas os métodos desejados."
        )

        overview_cols = st.columns(2)
        overview_cols[0].plotly_chart(build_runtime_comparison_chart(filtered_runs), use_container_width=True)
        overview_cols[1].plotly_chart(build_drift_summary_chart(filtered_runs), use_container_width=True)

        state_cols = st.columns(2)
        state_cols[0].plotly_chart(
            build_series_comparison_chart(filtered_runs, "distance_series", "Comparação da distância entre os corpos", "||r2 - r1||"),
            use_container_width=True,
        )
        state_cols[1].plotly_chart(
            build_series_comparison_chart(filtered_runs, "energy_series", "Comparação da energia total", "energia total"),
            use_container_width=True,
        )

        invariant_cols = st.columns(2)
        invariant_cols[0].plotly_chart(
            build_series_comparison_chart(filtered_runs, "angular_momentum_norm", "Comparação do módulo do momento angular total", "||L||"),
            use_container_width=True,
        )
        invariant_cols[1].plotly_chart(
            build_series_comparison_chart(filtered_runs, "linear_momentum_norm", "Comparação do módulo do momento linear total", "||P||"),
            use_container_width=True,
        )

    with details_tab:
        with st.expander("Configuração usada na rodada selecionada", expanded=True):
            st.json(active_run["config"])

        with st.expander("Persistência em arquivo"):
            st.write(f"Índice das rodadas: `{STREAMLIT_RUNS_INDEX_PATH}`")
            st.write(f"Arquivos numéricos: `{STREAMLIT_RUNS_DIR}`")


if __name__ == "__main__":
    main()
