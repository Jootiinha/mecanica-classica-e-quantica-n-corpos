import numpy as np
import matplotlib.pyplot as plt
from matplotlib import animation

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