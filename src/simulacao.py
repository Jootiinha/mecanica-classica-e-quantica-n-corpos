import numpy as np
from scipy.integrate import solve_ivp

from src.calculos import (
    equacao_newton_dois_corpos,
    massa_no_tempo,
)

FORMALISMS = ("newtonian",)
INTEGRATION_METHODS = ("DOP853", "RK45", "RK23", "Radau", "BDF", "LSODA")

def _validate_formalism(formalism: str) -> str:
    if formalism not in FORMALISMS:
        raise ValueError(f"Formalismo inválido: {formalism}")
    return formalism


def _validate_integration_method(method: str) -> str:
    normalized_method = method.strip()
    if normalized_method not in INTEGRATION_METHODS:
        raise ValueError(f"Metodo de integracao invalido: {method}")
    return normalized_method


def _build_initial_state(caso, formalism):
    physics = caso["physics"]

    initial_position_body_1 = np.array(physics["initial_position_body_1"], dtype=float)
    initial_position_body_2 = np.array(physics["initial_position_body_2"], dtype=float)
    initial_velocity_body_1 = np.array(physics["initial_velocity_body_1"], dtype=float)
    initial_velocity_body_2 = np.array(physics["initial_velocity_body_2"], dtype=float)
    center_mass_velocity = np.array(physics["center_mass_velocity"], dtype=float)

    initial_velocity_body_1 = initial_velocity_body_1 + center_mass_velocity
    initial_velocity_body_2 = initial_velocity_body_2 + center_mass_velocity

    return np.concatenate(
        (
            initial_position_body_1,
            initial_position_body_2,
            initial_velocity_body_1,
            initial_velocity_body_2,
        )
    )


def _extract_solution_arrays(solucao, m1_series, m2_series, formalism):
    r1_sol = solucao[:, 0:3]
    r2_sol = solucao[:, 3:6]
    v1_sol = solucao[:, 6:9]
    v2_sol = solucao[:, 9:12]
    p1_sol = m1_series[:, None] * v1_sol
    p2_sol = m2_series[:, None] * v2_sol

    return r1_sol, r2_sol, v1_sol, v2_sol, p1_sol, p2_sol


def simular_dois_corpos_3d(
    caso,
    formalism="newtonian",
    integration_method="DOP853",
    rtol=1e-10,
    atol=1e-10,
):
    formalism = _validate_formalism(formalism)
    integration_method = _validate_integration_method(integration_method)

    if caso['physics']['massa_variavel'] is True:
        if caso['physics']['tau1'] is None or caso['physics']['tau2'] is None:
            raise ValueError("Para massa variavel, tau1 e tau2 precisam ser definidos")

    init_parameters = _build_initial_state(caso, formalism)

    time_span = np.linspace(0.0, caso['physics']['t_final'], caso['physics']['n_pontos'])

    solver_object = solve_ivp(
        equacao_newton_dois_corpos,
        [0.0, caso['physics']['t_final']],
        init_parameters,
        t_eval=time_span,
        args=(
                caso['physics']['gravity']
            ,   caso['physics']['m1']
            ,   caso['physics']['m2']
            ,   caso['physics']['eps']
            ,   caso['physics']['massa_variavel']
            ,   caso['physics']['tau1']
            ,   caso['physics']['tau2']
        ),
        method=integration_method,
        rtol=rtol,
        atol=atol
    )

    if not solver_object.success:
        raise RuntimeError(f"Falha na integração ({formalism}): {solver_object.message}")

    solucao = solver_object.y.T

    m1_series = massa_no_tempo(time_span, caso['physics']['m1'], caso['physics']['tau1'], caso['physics']['massa_variavel'])
    m2_series = massa_no_tempo(time_span, caso['physics']['m2'], caso['physics']['tau2'], caso['physics']['massa_variavel'])
    r1_sol, r2_sol, v1_sol, v2_sol, p1_sol, p2_sol = _extract_solution_arrays(
        solucao,
        m1_series,
        m2_series,
        formalism,
    )

    r_com_sol = (
        m1_series[:, None] * r1_sol + m2_series[:, None] * r2_sol
    ) / (m1_series[:, None] + m2_series[:, None])

    return {
        "time": time_span,
        "r1": r1_sol,
        "r2": r2_sol,
        "v1": v1_sol,
        "v2": v2_sol,
        "p1": p1_sol,
        "p2": p2_sol,
        "r_com": r_com_sol,
        "m1_t": m1_series,
        "m2_t": m2_series,
        "formalism": np.array(formalism),
        "integration_method": np.array(integration_method),
        "rtol": np.array(float(rtol)),
        "atol": np.array(float(atol)),
        "nfev": np.array(int(solver_object.nfev)),
    }
