import numpy as np
from scipy.integrate import solve_ivp

from src.plot import render_simulation_artifacts

from src.calculos import (
        equacao_de_dois_corpos
    ,   massa_no_tempo
)

def simular_dois_corpos_3d(caso):

    if caso['physics']['massa_variavel'] == True:
        if caso['physics']['tau1'] is None or caso['physics']['tau2'] is None:
            raise ValueError("Para massa variavel, tau1 e tau2 precisam ser definidos")
    
    # Posição corpo 1
    initial_position_body_1 = np.array(caso['physics']['initial_position_body_1'], dtype=float)
    initial_position_body_2 = np.array(caso['physics']['initial_position_body_2'], dtype=float)
    
    # Posição corpo 2
    initial_velocity_body_1 = np.array(caso['physics']['initial_velocity_body_1'], dtype=float)
    initial_velocity_body_2 = np.array(caso['physics']['initial_velocity_body_2'], dtype=float)

    center_mass_velocity = np.array([0.0, 0.0, 0.0], dtype=float)
    
    # Soma de vetores
    initial_velocity_body_1 = initial_velocity_body_1 + center_mass_velocity
    initial_velocity_body_2 = initial_velocity_body_2 + center_mass_velocity

    init_parameters = np.concatenate(
        (initial_position_body_1, initial_position_body_2, initial_velocity_body_1, initial_velocity_body_2)
    )

    time_span = np.linspace(0.0, caso['physics']['t_final'], caso['physics']['n_pontos'])

    solver_object = solve_ivp(
        equacao_de_dois_corpos,
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
        method='DOP853',
        rtol=1e-10,
        atol=1e-10
    )

    solucao = solver_object.y.T

    r1_sol = solucao[:, 0:3]
    r2_sol = solucao[:, 3:6]

    m1_series = massa_no_tempo(time_span, caso['physics']['m1'], caso['physics']['tau1'], caso['physics']['massa_variavel'])
    m2_series = massa_no_tempo(time_span, caso['physics']['m2'], caso['physics']['tau2'], caso['physics']['massa_variavel'])

    r_com_sol = (
        m1_series[:, None] * r1_sol + m2_series[:, None] * r2_sol
    ) / (m1_series[:, None] + m2_series[:, None])

    render_simulation_artifacts(caso, time_span, r1_sol, r2_sol, r_com_sol)