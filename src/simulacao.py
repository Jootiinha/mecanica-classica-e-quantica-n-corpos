import numpy as np
import os
from scipy.integrate import solve_ivp
import matplotlib.pyplot as plt
from matplotlib import animation

from src.plot import set_axes_equal_3d
from src.utils import _slugify_nome_arquivo

from src.calculos import (
        posicao_centro_massa
    ,   velocidade_centro_massa
    ,   equacao_de_dois_corpos
    ,   massa_no_tempo
    ,   energial_total
    ,   momento_liner_total
    ,   momento_angular_total
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

    r_com_0 = posicao_centro_massa(caso['physics']['m1'], initial_position_body_1, caso['physics']['m2'], initial_position_body_2)
    v_com_0 = velocidade_centro_massa(caso['physics']['m1'], initial_velocity_body_1, caso['physics']['m2'], initial_velocity_body_2)

    init_parameters = np.concatenate(
        (initial_position_body_1, initial_position_body_2, initial_velocity_body_1, initial_velocity_body_2)
    )

    time_span = np.linspace(0.0, caso['physics']['t_final'], caso['physics']['n_pontos'])

    solver_object = solve_ivp(
        equacao_de_dois_corpos,
        [0.0, caso['physics']['t_final']],
        init_parameters,
        t_eval=time_span,
        args=(caso['physics']['gravity'], caso['physics']['m1'], caso['physics']['m2'], caso['physics']['eps'], caso['physics']['massa_variavel'], caso['physics']['tau1'], caso['physics']['tau2']),
        method='DOP853',
        rtol=1e-10,
        atol=1e-10
    )

    if not solver_object.success:
        print("A integração falhou")
        print(solver_object.message)
        raise ValueError("A integração falhou")

    print("Integração concluída.")
    
    solucao = solver_object.y.T

    r1_sol = solucao[:, 0:3]
    r2_sol = solucao[:, 3:6]

    v1_sol = solucao[:, 6:9]
    v2_sol = solucao[:, 9:12]

    m1_series = massa_no_tempo(time_span, caso['physics']['m1'], caso['physics']['tau1'], caso['physics']['massa_variavel'])
    m2_series = massa_no_tempo(time_span, caso['physics']['m2'], caso['physics']['tau2'], caso['physics']['massa_variavel'])

    r_com_sol = (
        m1_series[:, None] * r1_sol + m2_series[:, None] * r2_sol
    ) / (m1_series[:, None] + m2_series[:, None])

    E = energial_total(r1_sol, r2_sol, v1_sol, v2_sol, caso['physics']['gravity'], m1_series, m2_series, caso['physics']['eps'])
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
    ax_static.set_title(caso['name'], pad=20)

    ax_static.view_init(elev=25, azim=35)
    ax_static.legend(loc="lower left")

    set_axes_equal_3d(ax_static, r1_sol, r2_sol, r_com_sol, fator_visual_z=0.75)

    if caso['chart']['mostrar_grafico']:
        print("Exibindo gráfico estático...")
        plt.show()
    else:
        plt.close(fig_static)

    if not caso['chart']['salvar_animacao']:
        print("Exportação de animação desativada para este cenário.")
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
            "animacao": None,
            "video": None
        }

    writer_ffmpeg_disponivel = animation.writers.is_available("ffmpeg")
    skip_animacao = caso['chart']["skip"]
    dpi_animacao = caso['chart']["dpi"]

    if not writer_ffmpeg_disponivel:
        skip_animacao = max(skip_animacao, caso['chart']["skip_pillow"], 12)
        dpi_animacao = min(dpi_animacao, caso['chart']["dpi_pillow"], 100)

    # Animacao 3d
    print(
        f"Preparando animação com {('ffmpeg' if writer_ffmpeg_disponivel else 'pillow')} "
        f"(skip={skip_animacao}, dpi={dpi_animacao})..."
    )
    r1_anim = r1_sol[::skip_animacao]
    r2_anim = r2_sol[::skip_animacao]
    r_com_anim = r_com_sol[::skip_animacao]
    time_anim = time_span[::skip_animacao]

    frames = len(r1_anim)
    print(f"Total de frames da animação: {frames}")

    fig = plt.figure(figsize=(9, 8))
    ax = fig.add_subplot(111, projection="3d")

    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.set_zlabel("z")
    ax.set_title(caso['name'], pad=20)

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

    pasta_saida = os.path.join("outputs", "adhoc")
    os.makedirs(pasta_saida, exist_ok=True)
    base_nome_arquivo = _slugify_nome_arquivo(caso["name"])
    nome_video = None

    if writer_ffmpeg_disponivel:
        print("Salvando animação com ffmpeg...")
        nome_video = os.path.join(pasta_saida, f"{base_nome_arquivo}.mp4")
        Writer = animation.writers["ffmpeg"]
        writer = Writer(fps=caso['fps'], metadata=dict(artist="MCQ"), bitrate=4000)
        anim.save(
            nome_video,
            writer=writer,
            dpi=dpi_animacao,
            progress_callback=lambda i, n: print(f"Renderizando frame {i + 1}/{n}") if (i + 1) % 100 == 0 or i + 1 == n else None,
        )
        print("\nVídeo salvo como:", nome_video)
    elif animation.writers.is_available("pillow"):
        print("FFmpeg indisponível. Salvando animação com Pillow...")
        nome_video = os.path.join(pasta_saida, f"{base_nome_arquivo}.gif")
        writer = animation.PillowWriter(fps=caso['chart']['fps'], metadata=dict(artist="MCQ"))
        anim.save(
            nome_video,
            writer=writer,
            dpi=dpi_animacao,
            progress_callback=lambda i, n: print(f"Renderizando frame {i + 1}/{n}") if (i + 1) % 25 == 0 or i + 1 == n else None,
        )
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
