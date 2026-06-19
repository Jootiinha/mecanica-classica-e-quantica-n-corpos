from calculos import (
        posicao_centro_massa
    ,   velocidade_centro_massa
    ,   equacao_de_dois_corpos
    ,   massa_no_tempo
    ,   energial_total
    ,   momento_liner_total
    ,   momento_angular_total
)
from plot import set_axes_equal_3d
import numpy as np
from scipy.integrate import solve_ivp

import matplotlib.pyplot as plt
from matplotlib import animation


def _validar_vetor_3d(nome, valor, permitir_vazio=False):
    vetor = np.array(valor, dtype=float)

    if permitir_vazio and vetor.size == 0:
        return vetor

    if vetor.shape != (3,):
        raise ValueError(f"{nome} deve ter exatamente 3 coordenadas, recebido shape {vetor.shape}")

    return vetor


def simular_dois_corpos_3d(caso):
    # Salvar sempre o vídeo e o gráfico
    
    if caso['massa_variavel'] == True:
        if caso['tau1'] is None or caso['tau2'] is None:
            raise ValueError("Para massa variavel, tau1 e tau2 precisam ser definidos")
    
    # Posição corpo 1
    r1_0 = _validar_vetor_3d("r1", caso['r1'])
    r2_0 = _validar_vetor_3d("r2", caso['r2'])
    
    # Posição corpo 2
    v1_0 = _validar_vetor_3d("v1", caso['v1'])
    v2_0 = _validar_vetor_3d("v2", caso['v2'])

    V_CM = np.array([0.0, 0.0, 0.0], dtype=float)

    if caso['V_CM'] is not None:
        V_CM = _validar_vetor_3d("V_CM", caso['V_CM'], permitir_vazio=True)
        if V_CM.size == 0:
            V_CM = np.array([0.0, 0.0, 0.0], dtype=float)
    
    v1_0 = v1_0 + V_CM
    v2_0 = v2_0 + V_CM

    r_com_0 = posicao_centro_massa(caso['m1'], r1_0, caso['m2'], r2_0)
    v_com_0 = velocidade_centro_massa(caso['m1'], v1_0, caso['m2'], v2_0)

    print(12*'=')
    print(
        f"""
            G => {caso['G']} \n
            M1 INICIAL  \t\t\t {caso['m1']} \n
            M2 INICIAL \t\t\t {caso['m2']} \n
            m1/m2 INICIAL \t\t\t {caso['m1'] / caso['m2']} \n
            eps \t\t\t {caso['eps']} \n
            massa variavel \t\t\t {caso['massa_variavel']} \n
            tau1 \t\t\t {caso['tau1']} \n
            tau2 \t\t\t {caso['tau2']} \n
            m1(t_final)/m1(0) \t\t\t {np.exp(-caso['t_final'] / caso['tau1'])} \n
            m2(t_final)/m2(0) \t\t\t {np.exp(-caso['t_final'] / caso['tau2'])} \n
            V_CM \t\t\t {caso['V_CM']} \n
            r1(0) \t\t\t { r1_0} \n
            r2(0) \t\t\t { r2_0} \n
            v1(0) \t\t\t { v1_0 } \n
            v2(0) \t\t\t { v2_0} \n
            CM inicial \t\t\t { r_com_0 } \n
            V_CM inicial \t\t\t { v_com_0 } \n
        """
    )
    print(12*'=')

    init_parameters = np.concatenate(
        (r1_0, r2_0, v1_0, v2_0)
    )

    time_span = np.linspace(0.0, caso['t_final'], caso['n_pontos'])

    solver_object = solve_ivp(
        equacao_de_dois_corpos,
        [0.0, caso['t_final']],
        init_parameters,
        t_eval=time_span,
        args=(caso['G'], caso['m1'], caso['m2'], caso['eps'], caso['massa_variavel'], caso['tau1'], caso['tau2']),
        method='DOP853',
        rtol=1e-10,
        atol=1e-10
    )

    if not solver_object.success:
        print("A integração falhou")
        print(solver_object.message)
        raise ValueError("A integração falhou")
    
    solucao = solver_object.y.T

    r1_sol = solucao[:, 0:3]
    r2_sol = solucao[:, 3:6]

    v1_sol = solucao[:, 6:9]
    v2_sol = solucao[:, 9:12]

    m1_series = massa_no_tempo(time_span, caso['m1'], caso['tau1'], caso['massa_variavel'])
    m2_series = massa_no_tempo(time_span, caso['m2'], caso['tau2'], caso['massa_variavel'])

    r_com_sol = (
        m1_series[:, None] * r1_sol + m2_series[:, None] * r2_sol
    ) / (m1_series[:, None] + m2_series[:, None])

    E = energial_total(r1_sol, r2_sol, v1_sol, v2_sol, caso['G'], m1_series, m2_series, caso['eps'])
    P = momento_liner_total(v1_sol, v2_sol, m1_series, m2_series)
    L = momento_angular_total(r1_sol, r2_sol, v1_sol, v2_sol, m1_series, m2_series)

    E0 = E[0]
    Ef = E[-1]

    if abs(E[0]) > 1e-14:
        variacao_relativa_e = abs((Ef - E0) / E0)
    else:
        variacao_relativa_e = abs(Ef - E0)


    fig_static = plt.figure(figsize=(9, 8))
    ax_static = fig_static.add_subplot(111, projection="3d")

    ax_static.plot(r1_sol[:, 0], r1_sol[:, 1], r1_sol[:, 2], color="darkblue", label="Corpo 1")
    ax_static.plot(r2_sol[:, 0], r2_sol[:, 1], r2_sol[:, 2], color="red", label="Corpo 2")
    ax_static.plot(r_com_sol[:, 0], r_com_sol[:, 1], r_com_sol[:, 2], color="black", linestyle="--", label="Centro de massa")

    ax_static.scatter(r1_sol[0, 0], r1_sol[0, 1], r1_sol[0, 2], color="darkblue", s=80)
    ax_static.scatter(r2_sol[0, 0], r2_sol[0, 1], r2_sol[0, 2], color="red", s=80)
    ax_static.scatter(r_com_sol[0, 0], r_com_sol[0, 1], r_com_sol[0, 2], color="black", s=40)

    ax_static.set_xlabel("x")
    ax_static.set_ylabel("y")
    ax_static.set_zlabel("z")
    ax_static.set_title(caso['nome'], pad=20)

    ax_static.view_init(elev=25, azim=35)
    ax_static.legend(loc="lower left")

    set_axes_equal_3d(ax_static, r1_sol, r2_sol, r_com_sol, fator_visual_z=0.75)

    plt.show()
    

    # Animacao 3d
    r1_anim = r1_sol[::caso['skip']]
    r2_anim = r2_sol[::caso['skip']]
    r_com_anim = r_com_sol[::caso['skip']]
    time_anim = time_span[::caso['skip']]

    m1_anim = m1_series[::caso['skip']]

    m2_anim = m2_series[::caso['skip']]

    frames = len(r1_anim)

    fig = plt.figure(figsize=(9, 8))
    ax = fig.add_subplot(111, projection="3d")

    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.set_zlabel("z")
    ax.set_title(caso['nome'], pad=20)

    ax.view_init(elev=25, azim=35)

    set_axes_equal_3d(ax, r1_sol, r2_sol, r_com_sol, fator_visual_z=0.75)

    line1, = ax.plot([], [], [], color="darkblue", label="Corpo 1")
    line2, = ax.plot([], [], [], color="red", label="Corpo 2")
    line_com, = ax.plot([], [], [], color="black", linestyle="--", label="Centro de massa")

    point1, = ax.plot([], [], [], "o", color="darkblue", markersize=8)
    point2, = ax.plot([], [], [], "o", color="red", markersize=8)
    point_com, = ax.plot([], [], [], "o", color="black", markersize=5)

    ax.legend(loc="lower left")

    info_text = ax.text2D(
        0.98,
        0.95,
        "",
        transform=ax.transAxes,
        fontsize=10,
        ha="right",
        va="top",
        bbox=dict(facecolor='white', alpha=0.7, edgecolor='none', pad=5)
    )

    def init_animation():
        line1.set_data([], [])
        line1.set_3d_properties([])

        line2.set_data([], [])
        line2.set_3d_properties([])

        line_com.set_data([], [])
        line_com.set_3d_properties([])

        point1.set_data([], [])
        point1.set_3d_properties([])

        point2.set_data([], [])
        point2.set_3d_properties([])

        point_com.set_data([], [])
        point_com.set_3d_properties([])

        info_text.set_text("")

        return line1, line2, line_com, point1, point2, point_com, info_text

    def animate(i):
        line1.set_data(r1_anim[:i + 1, 0], r1_anim[:i + 1, 1])
        line1.set_3d_properties(r1_anim[:i + 1, 2])

        line2.set_data(r2_anim[:i + 1, 0], r2_anim[:i + 1, 1])
        line2.set_3d_properties(r2_anim[:i + 1, 2])

        line_com.set_data(r_com_anim[:i + 1, 0], r_com_anim[:i + 1, 1])
        line_com.set_3d_properties(r_com_anim[:i + 1, 2])

        point1.set_data([r1_anim[i, 0]], [r1_anim[i, 1]])
        point1.set_3d_properties([r1_anim[i, 2]])

        point2.set_data([r2_anim[i, 0]], [r2_anim[i, 1]])
        point2.set_3d_properties([r2_anim[i, 2]])

        point_com.set_data([r_com_anim[i, 0]], [r_com_anim[i, 1]])
        point_com.set_3d_properties([r_com_anim[i, 2]])

        info_text.set_text(f"t = {time_anim[i]:.2f}")

        ax.view_init(elev=25, azim=35)

        return line1, line2, line_com, point1, point2, point_com, info_text

    anim = animation.FuncAnimation(
        fig,
        animate,
        init_func=init_animation,
        frames=frames,
        interval=20,
        blit=False
    )

    nome_video = None

    if animation.writers.is_available("ffmpeg"):
        nome_video = "alec_simulacao.mp4"
        Writer = animation.writers["ffmpeg"]
        writer = Writer(fps=caso['fps'], metadata=dict(artist="MCQ"), bitrate=4000)
        anim.save(nome_video, writer=writer, dpi=caso['dpi'])
        print("\nVídeo salvo como:", nome_video)
    elif animation.writers.is_available("pillow"):
        nome_video = "alec_simulacao.gif"
        writer = animation.PillowWriter(fps=caso['fps'], metadata=dict(artist="MCQ"))
        anim.save(nome_video, writer=writer, dpi=caso['dpi'])
        print("\nFFmpeg indisponível. Animação salva como:", nome_video)
    else:
        print("\nNenhum writer de animação disponível. A simulação foi concluída sem exportar vídeo.")

    plt.close(fig)

    return {
        "time": time_span,
        "r1": r1_sol,
        "r2": r2_sol,
        "v1": v1_sol,
        "v2": v2_sol,
        "r_com": r_com_sol,
        "m1_t": m1_series,
        "m2_t": m2_series,
        "E": E,
        "P": P,
        "L": L,
        "animacao": anim,
        "video": nome_video
    }
