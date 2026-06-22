from __future__ import annotations

import copy
import json
import time
from pathlib import Path

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


def build_plot(result: dict, scenario_name: str, formalism: str, frame_index: int, stride: int) -> go.Figure:
    r1 = result["r1"][::stride]
    r2 = result["r2"][::stride]
    r_com = result["r_com"][::stride]

    selected_r1 = result["r1"][frame_index]
    selected_r2 = result["r2"][frame_index]
    selected_r_com = result["r_com"][frame_index]
    selected_time = float(result["time"][frame_index])

    fig = go.Figure()
    fig.add_trace(
        go.Scatter3d(
            x=r1[:, 0],
            y=r1[:, 1],
            z=r1[:, 2],
            mode="lines",
            name="Corpo 1",
            line=dict(color="#123c69", width=5),
        )
    )
    fig.add_trace(
        go.Scatter3d(
            x=r2[:, 0],
            y=r2[:, 1],
            z=r2[:, 2],
            mode="lines",
            name="Corpo 2",
            line=dict(color="#d1495b", width=5),
        )
    )
    fig.add_trace(
        go.Scatter3d(
            x=r_com[:, 0],
            y=r_com[:, 1],
            z=r_com[:, 2],
            mode="lines",
            name="Centro de massa",
            line=dict(color="#2f2f2f", width=4, dash="dash"),
        )
    )
    fig.add_trace(
        go.Scatter3d(
            x=[selected_r1[0], selected_r2[0], selected_r_com[0]],
            y=[selected_r1[1], selected_r2[1], selected_r_com[1]],
            z=[selected_r1[2], selected_r2[2], selected_r_com[2]],
            mode="markers",
            name="Posição atual",
            marker=dict(size=[7, 7, 5], color=["#123c69", "#d1495b", "#2f2f2f"]),
        )
    )

    fig.update_layout(
        title=f"{scenario_name} [{formalism}]",
        margin=dict(l=0, r=0, t=48, b=0),
        height=720,
        legend=dict(orientation="h", yanchor="bottom", y=0.02, xanchor="left", x=0.02),
        scene=dict(
            xaxis_title="x",
            yaxis_title="y",
            zaxis_title="z",
            aspectmode="data",
        ),
        annotations=[
            dict(
                x=0.99,
                y=0.99,
                xref="paper",
                yref="paper",
                text=f"t = {selected_time:.3f}",
                showarrow=False,
                bgcolor="rgba(255,255,255,0.85)",
            )
        ],
    )
    return fig


def main() -> None:
    st.set_page_config(
        page_title="Simulação Newtoniana Interativa",
        layout="wide",
    )

    st.title("Simulação gravitacional interativa")
    st.caption("Protótipo web para explorar cenários de dois corpos em tempo quase real.")

    scenario_names = list_scenarios()
    if not scenario_names:
        st.error("Nenhum arquivo YAML foi encontrado em ./scenarios.")
        return

    selected_scenario = st.sidebar.selectbox("Cenário base", scenario_names)
    default_config = copy.deepcopy(load_scenario_config(selected_scenario))
    physics = default_config["physics"]
    chart = default_config["chart"]

    st.sidebar.subheader("Execução")
    formalism = st.sidebar.selectbox("Formalismo", FORMALISMS, index=0)
    auto_run = st.sidebar.toggle("Atualizar automaticamente", value=True)
    preview_points = st.sidebar.slider("Pontos máximos no gráfico", 100, 4000, 800, step=100)

    st.sidebar.subheader("Parâmetros físicos")
    physics["gravity"] = st.sidebar.number_input("Constante gravitacional", value=float(physics["gravity"]), step=step_for_value(physics["gravity"], 0.01), format="%.6f")
    physics["eps"] = st.sidebar.number_input("Amortecimento eps", value=float(physics["eps"]), min_value=0.0, step=step_for_value(physics["eps"], 0.001), format="%.6f")
    physics["m1"] = st.sidebar.number_input("Massa do corpo 1", value=float(physics["m1"]), min_value=1e-9, step=step_for_value(physics["m1"]), format="%.6f")
    physics["m2"] = st.sidebar.number_input("Massa do corpo 2", value=float(physics["m2"]), min_value=1e-9, step=step_for_value(physics["m2"]), format="%.6f")
    physics["t_final"] = st.sidebar.number_input("Tempo final", value=float(physics["t_final"]), min_value=0.1, step=1.0, format="%.3f")
    physics["n_pontos"] = int(
        st.sidebar.slider("Quantidade de pontos", min_value=200, max_value=12000, value=int(physics["n_pontos"]), step=100)
    )
    physics["massa_variavel"] = st.sidebar.checkbox("Massa variável", value=bool(physics["massa_variavel"]))

    if physics["massa_variavel"]:
        physics["tau1"] = st.sidebar.number_input("Tau 1", value=float(physics["tau1"] or 1.0), min_value=0.001, step=1.0, format="%.6f")
        physics["tau2"] = st.sidebar.number_input("Tau 2", value=float(physics["tau2"] or 1.0), min_value=0.001, step=1.0, format="%.6f")
    else:
        physics["tau1"] = None
        physics["tau2"] = None

    st.subheader("Condições iniciais")
    physics["initial_position_body_1"] = vector_input("Posição inicial corpo 1", physics["initial_position_body_1"])
    physics["initial_position_body_2"] = vector_input("Posição inicial corpo 2", physics["initial_position_body_2"])
    physics["initial_velocity_body_1"] = vector_input("Velocidade inicial corpo 1", physics["initial_velocity_body_1"])
    physics["initial_velocity_body_2"] = vector_input("Velocidade inicial corpo 2", physics["initial_velocity_body_2"])
    physics["center_mass_velocity"] = vector_input("Velocidade do centro de massa", physics["center_mass_velocity"])

    st.subheader("Parâmetros de visualização")
    chart["fps"] = int(st.number_input("FPS de referência", value=int(chart["fps"]), min_value=1, max_value=120, step=1))
    chart["skip"] = int(st.number_input("Skip de render offline", value=int(chart["skip"]), min_value=1, max_value=100, step=1))
    chart["dpi"] = int(st.number_input("DPI de referência", value=int(chart["dpi"]), min_value=50, max_value=300, step=10))

    run_requested = auto_run or st.sidebar.button("Rodar simulação")
    if not run_requested:
        st.info("Ajuste os parâmetros e clique em 'Rodar simulação' para calcular.")
        return

    config_json = json.dumps(default_config, sort_keys=True)

    try:
        with st.spinner("Calculando trajetórias..."):
            result, elapsed = run_simulation_cached(config_json, formalism)
    except Exception as exc:
        st.error(f"Falha ao executar a simulação: {exc}")
        return

    total_points = len(result["time"])
    stride = max(1, total_points // preview_points)
    frame_index = st.slider("Instante analisado", 0, total_points - 1, total_points - 1)

    metric_cols = st.columns(4)
    metric_cols[0].metric("Tempo de cálculo", f"{elapsed:.3f}s")
    metric_cols[1].metric("Pontos integrados", total_points)
    metric_cols[2].metric("Preview plotado", len(result["time"][::stride]))
    metric_cols[3].metric("Formalismo", formalism)

    figure = build_plot(result, default_config["name"], formalism, frame_index, stride)
    st.plotly_chart(figure, use_container_width=True)

    details_cols = st.columns(3)
    selected_time = float(result["time"][frame_index])
    details_cols[0].write(f"**t selecionado:** {selected_time:.3f}")
    details_cols[1].write(f"**r1(t):** {result['r1'][frame_index].round(6).tolist()}")
    details_cols[2].write(f"**r2(t):** {result['r2'][frame_index].round(6).tolist()}")

    with st.expander("Configuração usada na simulação"):
        st.json(default_config)


if __name__ == "__main__":
    main()
