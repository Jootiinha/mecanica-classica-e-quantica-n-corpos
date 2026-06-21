import numpy as np

def posicao_centro_massa(m1, r1, m2, r2):
    return ( (m1 * r1) + (m2 * r2) ) / (m1 + m2)

def velocidade_centro_massa(m1, v1, m2, v2):
    return ( (m1 * v1) + (m2 * v2) ) / (m1 + m2)


def massa_no_tempo(t, m10, tau1, massa_variavel):
    # Massa constante m(t) = 0
    # Massa variavel m(t) = m0 * exp(-t/tau)

    t_array = np.asarray(t, dtype=float)

    if massa_variavel:
        massa = m10 * np.exp(-t_array / tau1)
    else:
        massa = np.full_like(t_array, m10, dtype=float)

    if massa.ndim == 0:
        return float(massa)
    
    return massa

def equacao_de_dois_corpos(
        t, # Tempo atual da simulação
        w, # Vetor do estado atual do sistema
        G, # Constante gravitacional
        m10, # Massa inicial do corpo 1
        m20, # massa inicial do corpo 2
        eps, # Suavização numérica da distância
        massa_variavel, # Massa variavel
        tau1, # Tempo característico de perda de massa dos corpos 1
        tau2 #Tempo característico de perda de massa dos corpos 2

):
    # w = [x1, y1, z1, x2, y2....]
    r1 = w[0:3]
    r2 = w[3:6]
    v1 = w[6:9]
    v2 = w[9:12]

    m1_t = massa_no_tempo(t, m10, tau1, massa_variavel)
    m2_t = massa_no_tempo(t, m20, tau2, massa_variavel)

    r12 = r2 - r1

    distancia = np.sqrt((np.dot(r12, r12) + eps**2))

    a1 = G * m2_t * r12 / distancia**3
    a2 = -G * m1_t * r12 / distancia**3


    return np.concatenate(
        (v1, v2, a1, a2)
    )



def energial_total(r1, r2, v1, v2, G, m1_series, m2_series, eps):
    r12 = r2 - r1

    dist = np.sqrt(np.sum(r12**2, axis=1) + eps**2)

    T = (
        0.5 * m1_series * np.sum(v1**2, axis=1) + 0.5 * m2_series * np.sum(v2**2, axis=1)
    )

    U = -G * m1_series * m2_series / dist

    return T + U



def momento_liner_total(v1, v2, m1_series, m2_series):
    return m1_series[:, None] * v1 + m2_series[:, None] * v2

def momento_angular_total(r1, r2, v1, v2, m1_series, m2_series):
    L1 = np.cross(r1, m1_series[:, None] * v1)
    L2 = np.cross(r2, m2_series[:, None] * v2)

    return L1 + L2
    
