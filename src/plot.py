import matplotlib.pyplot as plt
import numpy as np
import os
from matplotlib import animation
from matplotlib.lines import Line2D

from src.utils import _slugify_nome_arquivo, build_render_output_dir


def set_axes_equal_3d(ax, r1_sol, r2_sol, r_com_sol=None, fator_visual_z=0.75):
    """
    Ajusta os limites dos eixos 3D.

    fator_visual_z:
        - 1.00 mantém escala completamente igual.
        - menor que 1.00 deixa o eixo z visualmente mais destacado.
        - isso não altera a física, só o enquadramento visual.
    """

    arrays_x = [r1_sol[:, 0], r2_sol[:, 0]]
    arrays_y = [r1_sol[:, 1], r2_sol[:, 1]]
    arrays_z = [r1_sol[:, 2], r2_sol[:, 2]]

    if r_com_sol is not None:
        arrays_x.append(r_com_sol[:, 0])
        arrays_y.append(r_com_sol[:, 1])
        arrays_z.append(r_com_sol[:, 2])

    all_x = np.concatenate(arrays_x)
    all_y = np.concatenate(arrays_y)
    all_z = np.concatenate(arrays_z)

    x_min, x_max = all_x.min(), all_x.max()
    y_min, y_max = all_y.min(), all_y.max()
    z_min, z_max = all_z.min(), all_z.max()

    x_range = x_max - x_min
    y_range = y_max - y_min
    z_range = z_max - z_min

    max_range = max(x_range, y_range, z_range, 1.0)

    x_mid = 0.5 * (x_max + x_min)
    y_mid = 0.5 * (y_max + y_min)
    z_mid = 0.5 * (z_max + z_min)

    margin = 0.15
    lim = 0.5 * max_range * (1.0 + margin)

    ax.set_xlim(x_mid - lim, x_mid + lim)
    ax.set_ylim(y_mid - lim, y_mid + lim)
    ax.set_zlim(z_mid - lim * fator_visual_z, z_mid + lim * fator_visual_z)


def render_simulation_artifacts(
    caso,
    time_span,
    r1_sol,
    r2_sol,
    r_com_sol,
    formalism="newtonian",
    render_static=True,
):
    if render_static:
        _render_static_plot(caso, r1_sol, r2_sol, r_com_sol, formalism)

    if not caso["chart"]["salvar_animacao"]:
        print("Exportação de animação desativada para este cenário.")
        return {"animacao": None, "video": None}

    return _render_animation(
        caso,
        time_span,
        r1_sol,
        r2_sol,
        r_com_sol,
        formalism,
    )


def _format_param_value(value):
    if value is None:
        return "-"
    if isinstance(value, bool):
        return "sim" if value else "nao"
    if isinstance(value, (int, np.integer)):
        return str(value)
    if isinstance(value, (float, np.floating)):
        if float(value).is_integer():
            return str(int(value))
        return f"{value:.3g}"
    return str(value)


def _build_plot_title(caso, formalism):
    scenario_name = caso["name"]
    suffix = f" [{formalism}]"
    if scenario_name.endswith(suffix):
        scenario_name = scenario_name[: -len(suffix)]

    return f"Simulacao gravitacional 3D\n{scenario_name} | Formalismo: Newtoniano"


def _build_parameter_labels(caso):
    physics = caso["physics"]
    labels = [
        f"G={_format_param_value(physics['gravity'])} | eps={_format_param_value(physics['eps'])}",
        f"m1={_format_param_value(physics['m1'])} | m2={_format_param_value(physics['m2'])}",
        f"t_final={_format_param_value(physics['t_final'])} | n={_format_param_value(physics['n_pontos'])}",
    ]

    if physics["massa_variavel"]:
        labels.append(
            "massa variavel=sim"
            f" | tau1={_format_param_value(physics['tau1'])}"
            f" | tau2={_format_param_value(physics['tau2'])}"
        )
    else:
        labels.append("massa variavel=nao")

    return labels


def _add_legends(ax, caso):
    series_legend = ax.legend(loc="lower left", title="Trajetorias")
    ax.add_artist(series_legend)

    parameter_handles = [
        Line2D([], [], linestyle="none", marker=None, label=label)
        for label in _build_parameter_labels(caso)
    ]
    ax.legend(
        handles=parameter_handles,
        loc="upper left",
        bbox_to_anchor=(0.02, 0.98),
        borderaxespad=0.0,
        framealpha=0.9,
        title="Parametros",
        handlelength=0,
        handletextpad=0,
        fontsize=9,
    )


def _render_static_plot(caso, r1_sol, r2_sol, r_com_sol, formalism):
    fig_static = plt.figure(figsize=(9, 8))
    ax_static = fig_static.add_subplot(111, projection="3d")

    ax_static.plot(r1_sol[:, 0], r1_sol[:, 1], r1_sol[:, 2], color="darkblue", label="Corpo 1")
    ax_static.plot(r2_sol[:, 0], r2_sol[:, 1], r2_sol[:, 2], color="red", label="Corpo 2")
    ax_static.plot(
        r_com_sol[:, 0],
        r_com_sol[:, 1],
        r_com_sol[:, 2],
        color="black",
        linestyle="--",
        label="Centro de massa",
    )

    ax_static.scatter(r1_sol[0, 0], r1_sol[0, 1], r1_sol[0, 2], color="darkblue", s=80)
    ax_static.scatter(r2_sol[0, 0], r2_sol[0, 1], r2_sol[0, 2], color="red", s=80)
    ax_static.scatter(r_com_sol[0, 0], r_com_sol[0, 1], r_com_sol[0, 2], color="black", s=40)

    ax_static.set_xlabel("x")
    ax_static.set_ylabel("y")
    ax_static.set_zlabel("z")
    ax_static.set_title(_build_plot_title(caso, formalism), pad=24)
    ax_static.view_init(elev=25, azim=35)
    _add_legends(ax_static, caso)

    set_axes_equal_3d(ax_static, r1_sol, r2_sol, r_com_sol, fator_visual_z=0.75)
    fig_static.tight_layout()

    if caso["chart"]["mostrar_grafico"]:
        print("Exibindo gráfico estático...")
        plt.show()
        return

    plt.close(fig_static)


def _render_animation(
    caso,
    time_span,
    r1_sol,
    r2_sol,
    r_com_sol,
    formalism,
):
    writer_ffmpeg_disponivel = animation.writers.is_available("ffmpeg")
    skip_animacao = caso["chart"]["skip"]
    dpi_animacao = caso["chart"]["dpi"]

    if not writer_ffmpeg_disponivel:
        skip_animacao = max(skip_animacao, caso["chart"]["skip_pillow"], 12)
        dpi_animacao = min(dpi_animacao, caso["chart"]["dpi_pillow"], 100)

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
    ax.set_title(_build_plot_title(caso, formalism), pad=24)
    ax.view_init(elev=25, azim=35)

    set_axes_equal_3d(ax, r1_sol, r2_sol, r_com_sol, fator_visual_z=0.75)

    line1, = ax.plot([], [], [], color="darkblue", label="Corpo 1")
    line2, = ax.plot([], [], [], color="red", label="Corpo 2")
    line_com, = ax.plot([], [], [], color="black", linestyle="--", label="Centro de massa")
    point1, = ax.plot([], [], [], "o", color="darkblue", markersize=8)
    point2, = ax.plot([], [], [], "o", color="red", markersize=8)
    point_com, = ax.plot([], [], [], "o", color="black", markersize=5)
    _add_legends(ax, caso)
    fig.tight_layout()

    info_text = ax.text2D(
        0.98,
        0.95,
        "",
        transform=ax.transAxes,
        fontsize=10,
        ha="right",
        va="top",
        bbox=dict(facecolor="white", alpha=0.7, edgecolor="none", pad=5),
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
        line1.set_data(r1_anim[: i + 1, 0], r1_anim[: i + 1, 1])
        line1.set_3d_properties(r1_anim[: i + 1, 2])
        line2.set_data(r2_anim[: i + 1, 0], r2_anim[: i + 1, 1])
        line2.set_3d_properties(r2_anim[: i + 1, 2])
        line_com.set_data(r_com_anim[: i + 1, 0], r_com_anim[: i + 1, 1])
        line_com.set_3d_properties(r_com_anim[: i + 1, 2])
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
        blit=False,
    )

    nome_video = _save_animation(
        caso,
        anim,
        writer_ffmpeg_disponivel,
        dpi_animacao,
        fig,
        formalism,
    )
    plt.close(fig)
    return {"animacao": anim, "video": nome_video}


def _save_animation(caso, anim, writer_ffmpeg_disponivel, dpi_animacao, fig, formalism):
    pasta_saida = build_render_output_dir(formalism)
    pasta_saida.mkdir(parents=True, exist_ok=True)
    base_nome_arquivo = _slugify_nome_arquivo(caso["name"])

    if writer_ffmpeg_disponivel:
        print("Salvando animação com ffmpeg...")
        nome_video = pasta_saida / f"{base_nome_arquivo}.mp4"
        writer_cls = animation.writers["ffmpeg"]
        writer = writer_cls(fps=caso["chart"]["fps"], metadata=dict(artist="MCQ"), bitrate=4000)
        anim.save(
            str(nome_video),
            writer=writer,
            dpi=dpi_animacao,
            progress_callback=lambda i, n: print(f"Renderizando frame {i + 1}/{n}")
            if (i + 1) % 100 == 0 or i + 1 == n
            else None,
        )
        print("\nVídeo salvo como:", nome_video)
        return str(nome_video)

    if animation.writers.is_available("pillow"):
        print("FFmpeg indisponível. Salvando animação com Pillow...")
        nome_video = pasta_saida / f"{base_nome_arquivo}.gif"
        writer = animation.PillowWriter(fps=caso["chart"]["fps"], metadata=dict(artist="MCQ"))
        anim.save(
            str(nome_video),
            writer=writer,
            dpi=dpi_animacao,
            progress_callback=lambda i, n: print(f"Renderizando frame {i + 1}/{n}")
            if (i + 1) % 25 == 0 or i + 1 == n
            else None,
        )
        print("\nFFmpeg indisponível. Animação salva como:", nome_video)
        return str(nome_video)

    print("\nNenhum writer de animação disponível. A simulação foi concluída sem exportar vídeo.")
    plt.close(fig)
    return None
