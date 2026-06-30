from __future__ import annotations

import copy
import json
import time
from pathlib import Path

import numpy as np
import plotly.graph_objects as go
import streamlit as st

from src.simulacao import FORMALISMS, simular_dois_corpos_3d
from src.utils import load_scenarios

SCENARIOS_DIR = Path("scenarios")


@st.cache_data(show_spinner=False)
def list_scenarios() -> list[str]:
    return sorted(path.name for path in SCENARIOS_DIR.glob("*.yaml"))


@st.cache_data(show_spinner=False)
def load_scenario_config(scenario_name: str) -> dict:
    return load_scenarios(str(SCENARIOS_DIR / scenario_name))


@st.cache_data(show_spinner=False)
def run_simulation_cached(config_json: str, formalism: str) -> tuple[dict, float]:
    scenario_config = json.loads(config_json)
    start = time.perf_counter()
    result = simular_dois_corpos_3d(scenario_config, formalism=formalism)
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


def build_animated_plot(
    result: dict,
    scenario_name: str,
    formalism: str,
    stride: int,
    playback_ms: int,
) -> go.Figure:
    r1 = result["r1"][::stride]
    r2 = result["r2"][::stride]
    r_com = result["r_com"][::stride]
    time_points = result["time"][::stride]
    axis_ranges = _axis_ranges(result)
    total_frames = len(time_points)

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
            go.Scatter3d(
                x=r1[:1, 0],
                y=r1[:1, 1],
                z=r1[:1, 2],
                mode="lines",
                name="Corpo 1",
                line=dict(color="#123c69", width=6),
            ),
            go.Scatter3d(
                x=r2[:1, 0],
                y=r2[:1, 1],
                z=r2[:1, 2],
                mode="lines",
                name="Corpo 2",
                line=dict(color="#d1495b", width=6),
            ),
            go.Scatter3d(
                x=r_com[:1, 0],
                y=r_com[:1, 1],
                z=r_com[:1, 2],
                mode="lines",
                name="Centro de massa",
                line=dict(color="#ffffff", width=4, dash="dash"),
            ),
            marker_trace(0),
        ],
        frames=[
            go.Frame(
                name=str(index),
                data=[
                    go.Scatter3d(
                        x=r1[: index + 1, 0],
                        y=r1[: index + 1, 1],
                        z=r1[: index + 1, 2],
                        mode="lines",
                        line=dict(color="#123c69", width=6),
                    ),
                    go.Scatter3d(
                        x=r2[: index + 1, 0],
                        y=r2[: index + 1, 1],
                        z=r2[: index + 1, 2],
                        mode="lines",
                        line=dict(color="#d1495b", width=6),
                    ),
                    go.Scatter3d(
                        x=r_com[: index + 1, 0],
                        y=r_com[: index + 1, 1],
                        z=r_com[: index + 1, 2],
                        mode="lines",
                        line=dict(color="#ffffff", width=4, dash="dash"),
                    ),
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
        title=f"{scenario_name} [{formalism}]",
        height=820,
        margin=dict(l=0, r=0, t=56, b=0),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=0.02,
            xanchor="left",
            x=0.02,
            bgcolor="rgba(255,255,255,0.72)",
        ),
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
                y=1.08,
                showactive=False,
                buttons=[
                    dict(
                        label="Play",
                        method="animate",
                        args=[
                            None,
                            {
                                "frame": {"duration": playback_ms, "redraw": True},
                                "transition": {"duration": 0},
                                "fromcurrent": True,
                            },
                        ],
                    ),
                    dict(
                        label="Pause",
                        method="animate",
                        args=[
                            [None],
                            {
                                "frame": {"duration": 0, "redraw": True},
                                "transition": {"duration": 0},
                                "mode": "immediate",
                            },
                        ],
                    ),
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
                        "args": [
                            [str(index)],
                            {
                                "frame": {"duration": 0, "redraw": True},
                                "transition": {"duration": 0},
                                "mode": "immediate",
                            },
                        ],
                    }
                    for index in range(total_frames)
                ],
            )
        ],
    )
    return fig


def main() -> None:
    st.set_page_config(
        page_title="Simulação gravitacional animada",
        layout="wide",
    )

    st.title("Simulação gravitacional animada")
    st.caption("Ajuste os parâmetros e a animação 3D será recalculada automaticamente.")

    scenario_names = list_scenarios()
    if not scenario_names:
        st.error("Nenhum arquivo YAML foi encontrado em ./scenarios.")
        return

    st.sidebar.header("Cenário e solver")
    selected_scenario = st.sidebar.selectbox("Cenário base", scenario_names)
    default_config = copy.deepcopy(load_scenario_config(selected_scenario))
    physics = default_config["physics"]

    formalism = st.sidebar.selectbox("Formalismo", FORMALISMS, index=0)
    preview_points = st.sidebar.slider("Máximo de frames na animação", 60, 300, 180, step=20)
    playback_ms = st.sidebar.slider("Velocidade da animação (ms/frame)", 25, 250, 60, step=5)

    st.sidebar.header("Parâmetros físicos")
    physics["gravity"] = st.sidebar.number_input(
        "Constante gravitacional",
        value=float(physics["gravity"]),
        step=step_for_value(physics["gravity"], 0.01),
        format="%.6f",
    )
    physics["eps"] = st.sidebar.number_input(
        "Amortecimento eps",
        value=float(physics["eps"]),
        min_value=0.0,
        step=step_for_value(physics["eps"], 0.001),
        format="%.6f",
    )
    physics["m1"] = st.sidebar.number_input(
        "Massa do corpo 1",
        value=float(physics["m1"]),
        min_value=1e-9,
        step=step_for_value(physics["m1"]),
        format="%.6f",
    )
    physics["m2"] = st.sidebar.number_input(
        "Massa do corpo 2",
        value=float(physics["m2"]),
        min_value=1e-9,
        step=step_for_value(physics["m2"]),
        format="%.6f",
    )
    physics["t_final"] = st.sidebar.number_input(
        "Tempo final",
        value=float(physics["t_final"]),
        min_value=0.1,
        step=1.0,
        format="%.3f",
    )
    physics["n_pontos"] = int(
        st.sidebar.slider(
            "Quantidade de pontos",
            min_value=200,
            max_value=12000,
            value=int(physics["n_pontos"]),
            step=100,
        )
    )
    physics["massa_variavel"] = st.sidebar.checkbox(
        "Massa variável",
        value=bool(physics["massa_variavel"]),
    )

    if physics["massa_variavel"]:
        physics["tau1"] = st.sidebar.number_input(
            "Tau 1",
            value=float(physics["tau1"] or 1.0),
            min_value=0.001,
            step=1.0,
            format="%.6f",
        )
        physics["tau2"] = st.sidebar.number_input(
            "Tau 2",
            value=float(physics["tau2"] or 1.0),
            min_value=0.001,
            step=1.0,
            format="%.6f",
        )
    else:
        physics["tau1"] = None
        physics["tau2"] = None

    st.subheader("Condições iniciais")
    physics["initial_position_body_1"] = vector_input(
        "Posição inicial corpo 1",
        physics["initial_position_body_1"],
    )
    physics["initial_position_body_2"] = vector_input(
        "Posição inicial corpo 2",
        physics["initial_position_body_2"],
    )
    physics["initial_velocity_body_1"] = vector_input(
        "Velocidade inicial corpo 1",
        physics["initial_velocity_body_1"],
    )
    physics["initial_velocity_body_2"] = vector_input(
        "Velocidade inicial corpo 2",
        physics["initial_velocity_body_2"],
    )
    physics["center_mass_velocity"] = vector_input(
        "Velocidade do centro de massa",
        physics["center_mass_velocity"],
    )

    config_json = json.dumps(default_config, sort_keys=True)

    try:
        with st.spinner("Recalculando a simulação..."):
            result, elapsed = run_simulation_cached(config_json, formalism)
    except Exception as exc:
        st.error(f"Falha ao executar a simulação: {exc}")
        return

    total_points = len(result["time"])
    stride = max(1, total_points // preview_points)
    animated_points = len(result["time"][::stride])

    metrics = st.columns(4)
    metrics[0].metric("Tempo de cálculo", f"{elapsed:.3f}s")
    metrics[1].metric("Pontos integrados", total_points)
    metrics[2].metric("Frames exibidos", animated_points)
    metrics[3].metric("Formalismo", formalism)

    st.caption(
        "A interface recalcula automaticamente a dinâmica após cada ajuste e reduz a densidade "
        "de frames no navegador para manter a animação fluida."
    )
    st.plotly_chart(
        build_animated_plot(
            result,
            default_config["name"],
            formalism,
            stride,
            playback_ms,
        ),
        use_container_width=True,
    )

    with st.expander("Configuração usada na simulação"):
        st.json(default_config)


if __name__ == "__main__":
    main()
