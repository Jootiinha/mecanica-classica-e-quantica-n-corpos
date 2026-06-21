import numpy as np


def posicao_centro_massa(m1, r1, m2, r2):
    return ( (m1 * r1) + (m2 * r2) ) / (m1 + m2)


def velocidade_centro_massa(m1, v1, m2, v2):
    return ( (m1 * v1) + (m2 * v2) ) / (m1 + m2)


def massa_no_tempo(t, m10, tau1, massa_variavel):
    # Massa constante m(t) = m0
    # Massa variavel m(t) = m0 * exp(-t/tau)

    t_array = np.asarray(t, dtype=float)

    if massa_variavel:
        massa = m10 * np.exp(-t_array / tau1)
    else:
        massa = np.full_like(t_array, m10, dtype=float)

    if massa.ndim == 0:
        return float(massa)
    
    return massa


def aceleracoes_gravitacionais(r1, r2, G, m1_t, m2_t, eps):
    r12 = r2 - r1
    distancia = np.sqrt(np.dot(r12, r12) + eps**2)

    a1 = G * m2_t * r12 / distancia**3
    a2 = -G * m1_t * r12 / distancia**3
    return a1, a2


def equacao_newton_dois_corpos(
        t,
        w,
        G,
        m10,
        m20,
        eps,
        massa_variavel,
        tau1,
        tau2
):
    r1 = w[0:3]
    r2 = w[3:6]
    v1 = w[6:9]
    v2 = w[9:12]

    m1_t = massa_no_tempo(t, m10, tau1, massa_variavel)
    m2_t = massa_no_tempo(t, m20, tau2, massa_variavel)

    a1, a2 = aceleracoes_gravitacionais(r1, r2, G, m1_t, m2_t, eps)

    return np.concatenate(
        (v1, v2, a1, a2)
    )


def equacao_lagrange_dois_corpos(
        t,
        w,
        G,
        m10,
        m20,
        eps,
        massa_variavel,
        tau1,
        tau2
):
    # Para este problema, as equações de Euler-Lagrange levam à mesma dinâmica
    # em coordenadas cartesianas quando integradas como sistema de primeira ordem.
    return equacao_newton_dois_corpos(t, w, G, m10, m20, eps, massa_variavel, tau1, tau2)


def equacao_hamilton_dois_corpos(
        t,
        w,
        G,
        m10,
        m20,
        eps,
        massa_variavel,
        tau1,
        tau2
):
    r1 = w[0:3]
    r2 = w[3:6]
    p1 = w[6:9]
    p2 = w[9:12]

    m1_t = massa_no_tempo(t, m10, tau1, massa_variavel)
    m2_t = massa_no_tempo(t, m20, tau2, massa_variavel)

    v1 = p1 / m1_t
    v2 = p2 / m2_t
    a1, a2 = aceleracoes_gravitacionais(r1, r2, G, m1_t, m2_t, eps)

    dp1_dt = m1_t * a1
    dp2_dt = m2_t * a2

    return np.concatenate((v1, v2, dp1_dt, dp2_dt))


def equacao_de_dois_corpos(
        t,
        w,
        G,
        m10,
        m20,
        eps,
        massa_variavel,
        tau1,
        tau2
):
    return equacao_newton_dois_corpos(t, w, G, m10, m20, eps, massa_variavel, tau1, tau2)


def hamiltoniano_total(r1, r2, p1, p2, G, m1_series, m2_series, eps):
    r12 = r2 - r1
    dist = np.sqrt(np.sum(r12**2, axis=1) + eps**2)

    T = (
        np.sum(p1**2, axis=1) / (2.0 * m1_series)
        + np.sum(p2**2, axis=1) / (2.0 * m2_series)
    )
    U = -G * m1_series * m2_series / dist
    return T + U



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
    
