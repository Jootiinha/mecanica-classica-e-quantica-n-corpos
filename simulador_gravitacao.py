import numpy as np
import os

def simular_gravitacao__2d(g, m1, m2, r1_init, r2_init, v1_init, v2_init, total_passos, dt):
    M_total = m1 + m2

    # historico_r guardará matrizes 2x2 para cada passo: [[x1, y1], [x2, y2]]
    historico_r = np.zeros((total_passos, 2, 2))
    historico_Rcm = np.zeros((total_passos, 2))
    historico_Vcm = np.zeros((total_passos, 2))

    # Inicializando as variáveis de estado
    r1 = np.array(r1_init, dtype=float)
    r2 = np.array(r2_init, dtype=float)
    v1 = np.array(v1_init, dtype=float)
    v2 = np.array(v2_init, dtype=float)

    passos_executados = total_passos

    for i in range(total_passos):
        # Vetor distância
        dr = r2 - r1
        distancia = np.linalg.norm(dr) 

        if distancia < 0.01:  # Evita divisão por zero em colisões
            passos_executados = i
            break

        # CALCULA F (Utilizando vetor unitário para direção correta)
        f_intensidade = (g * m1 * m2) / (distancia**2)
        vetor_unitario = dr / distancia

        F1 = f_intensidade * vetor_unitario  # Força em 1 puxando para 2
        F2 = -F1                             # Força em 2 puxando para 1 (Ação e Reação)

        # CALCULA aceleração -> F = m * a
        a1 = F1 / m1
        a2 = F2 / m2

        # CALCULA velocidade -> v = v0 + a * dt
        v1 = v1 + a1 * dt
        v2 = v2 + a2 * dt

        # CALCULA posição -> r = r0 + v * dt
        r1 = r1 + v1 * dt
        r2 = r2 + v2 * dt

        # CALCULA Centro de Massa (Posição e Velocidade)
        Rcm = (m1 * r1 + m2 * r2) / M_total
        Vcm = (m1 * v1 + m2 * v2) / M_total

        # SALVA NAS MATRIZES PRÉ-ALOCADAS (Muito rápido)
        historico_r[i] = np.array([r1, r2])
        historico_Rcm[i] = Rcm
        historico_Vcm[i] = Vcm

    # Ajusta o tamanho caso tenha ocorrido colisão antes do fim do loop
    return (historico_r[:passos_executados], 
            historico_Rcm[:passos_executados], 
            historico_Vcm[:passos_executados])
