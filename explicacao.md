# Explicação do Código e da Matemática

## Visão geral

O projeto resolve numericamente o problema gravitacional de dois corpos e organiza a execução em três formalismos:

- `newtonian`
- `lagrangian`
- `hamiltonian`

A ideia central é sempre a mesma: dado um conjunto de condições iniciais, o programa integra o sistema no tempo e salva:

- trajetória dos corpos;
- velocidades ou momentos;
- centro de massa;
- métricas de performance;
- relatórios de conservação e comparação.

## 1. Problema físico

Temos dois corpos com massas `m1` e `m2`, posições `r1(t)` e `r2(t)` e interação gravitacional.

No código, isso aparece nos cenários YAML em `physics`:

- `m1`, `m2`
- `initial_position_body_1`, `initial_position_body_2`
- `initial_velocity_body_1`, `initial_velocity_body_2`
- `center_mass_velocity`
- `gravity`
- `eps`
- `t_final`
- `n_pontos`

Arquivos principais:

- [src/simulacao.py](/Users/joaocrm/Documents/dev/mestrado/mecanica-classica-e-quantica-n-corpos/src/simulacao.py:1)
- [src/calculos.py](/Users/joaocrm/Documents/dev/mestrado/mecanica-classica-e-quantica-n-corpos/src/calculos.py:1)

## 2. Força gravitacional

A base matemática do projeto está na Lei da Gravitação Universal de Newton:

```text
F = G * m1 * m2 / r^2
```

Como o código trabalha com vetores, ele usa a forma vetorial da aceleração:

```text
a1 = G * m2 * (r2 - r1) / |r2 - r1|^3
a2 = -G * m1 * (r2 - r1) / |r2 - r1|^3
```

No código:

- [src/calculos.py](/Users/joaocrm/Documents/dev/mestrado/mecanica-classica-e-quantica-n-corpos/src/calculos.py:27): `aceleracoes_gravitacionais(...)`

### Papel de `eps`

O termo `eps` entra como suavização numérica:

```text
distancia = sqrt((r2 - r1)·(r2 - r1) + eps^2)
```

Isso evita divisão por zero ou explosão numérica quando os corpos ficam muito próximos.

No código:

- [src/calculos.py](/Users/joaocrm/Documents/dev/mestrado/mecanica-classica-e-quantica-n-corpos/src/calculos.py:29)

## 3. Formalismo newtoniano

No formalismo newtoniano, o estado do sistema é:

```text
w = [r1, r2, v1, v2]
```

As equações integradas são:

```text
dr1/dt = v1
dr2/dt = v2
dv1/dt = a1
dv2/dt = a2
```

Pseudocódigo da etapa newtoniana:

```text
função equacao_newton_dois_corpos(t, w, G, m10, m20, eps, massa_variavel, tau1, tau2):
    r1 <- w[0:3]
    r2 <- w[3:6]
    v1 <- w[6:9]
    v2 <- w[9:12]

    m1_t <- massa_no_tempo(t, m10, tau1, massa_variavel)
    m2_t <- massa_no_tempo(t, m20, tau2, massa_variavel)

    r12 <- r2 - r1
    distancia <- sqrt(r12 · r12 + eps^2)

    a1 <- G * m2_t * r12 / distancia^3
    a2 <- -G * m1_t * r12 / distancia^3

    retornar [v1, v2, a1, a2]
```

No código:

- [src/calculos.py](/Users/joaocrm/Documents/dev/mestrado/mecanica-classica-e-quantica-n-corpos/src/calculos.py:36): `equacao_newton_dois_corpos(...)`

## 4. Formalismo lagrangiano

No problema de dois corpos em coordenadas cartesianas, as equações de Euler-Lagrange levam à mesma dinâmica física do caso newtoniano quando o sistema é escrito como EDO de primeira ordem.

A Lagrangiana é:

```text
L = T - U
```

onde:

```text
T = 1/2 m1 |v1|^2 + 1/2 m2 |v2|^2
U = - G m1 m2 / r
```

Por isso, neste projeto, o solver lagrangiano reaproveita a mesma dinâmica numérica do solver newtoniano.

No código:

- [src/calculos.py](/Users/joaocrm/Documents/dev/mestrado/mecanica-classica-e-quantica-n-corpos/src/calculos.py:59): `equacao_lagrange_dois_corpos(...)`

### Como explicar isso na apresentação

Você pode dizer:

- o formalismo lagrangiano foi usado no nível conceitual;
- para integração numérica, a dinâmica foi convertida ao mesmo sistema de primeira ordem;
- por isso as trajetórias coincidem com o formalismo newtoniano.

## 5. Formalismo hamiltoniano

No formalismo hamiltoniano, o estado do sistema muda para:

```text
w = [r1, r2, p1, p2]
```

em que:

```text
p1 = m1 v1
p2 = m2 v2
```

As equações de Hamilton ficam:

```text
dr1/dt = p1 / m1
dr2/dt = p2 / m2
dp1/dt = F1
dp2/dt = F2
```

No código:

- [src/calculos.py](/Users/joaocrm/Documents/dev/mestrado/mecanica-classica-e-quantica-n-corpos/src/calculos.py:74): `equacao_hamilton_dois_corpos(...)`
- [src/simulacao.py](/Users/joaocrm/Documents/dev/mestrado/mecanica-classica-e-quantica-n-corpos/src/simulacao.py:34): montagem do estado inicial com momentos

## 6. Massa variável

O trabalho também pede um caso com massa dependente do tempo.

O modelo adotado foi exponencial:

```text
m(t) = m0 * exp(-t / tau)
```

No código:

- [src/calculos.py](/Users/joaocrm/Documents/dev/mestrado/mecanica-classica-e-quantica-n-corpos/src/calculos.py:9): `massa_no_tempo(...)`

Se `massa_variavel` for `false`, a massa fica constante:

```text
m(t) = m0
```

## 7. Construção do estado inicial

O código lê o cenário YAML e monta o vetor inicial.

Para Newton e Lagrange:

```text
[r1(0), r2(0), v1(0), v2(0)]
```

Para Hamilton:

```text
[r1(0), r2(0), p1(0), p2(0)]
```

Além disso, a velocidade do centro de massa é somada às velocidades iniciais:

```text
v1(0) <- v1(0) + V_CM
v2(0) <- v2(0) + V_CM
```

No código:

- [src/simulacao.py](/Users/joaocrm/Documents/dev/mestrado/mecanica-classica-e-quantica-n-corpos/src/simulacao.py:22): `_build_initial_state(...)`

## 8. Integração numérica

Depois de montar o estado inicial, o programa cria a malha temporal:

```text
t = linspace(0, t_final, n_pontos)
```

e usa `solve_ivp` com método `DOP853`.

No código:

- [src/simulacao.py](/Users/joaocrm/Documents/dev/mestrado/mecanica-classica-e-quantica-n-corpos/src/simulacao.py:75)

### Interpretação prática

- `t_final`: tempo total da simulação
- `n_pontos`: quantidade de amostras salvas
- `rtol` e `atol`: tolerâncias numéricas

## 9. Centro de massa

O centro de massa é calculado por:

```text
r_com = (m1 r1 + m2 r2) / (m1 + m2)
```

No código:

- [src/calculos.py](/Users/joaocrm/Documents/dev/mestrado/mecanica-classica-e-quantica-n-corpos/src/calculos.py:4): fórmula auxiliar
- [src/simulacao.py](/Users/joaocrm/Documents/dev/mestrado/mecanica-classica-e-quantica-n-corpos/src/simulacao.py:106): cálculo da série temporal `r_com`

## 10. Grandezas conservadas

O projeto calcula três grandezas para avaliar a conservação numérica.

### Energia total

```text
E = T + U
```

com:

```text
T = 1/2 m1 |v1|^2 + 1/2 m2 |v2|^2
U = - G m1 m2 / r
```

No código:

- [src/calculos.py](/Users/joaocrm/Documents/dev/mestrado/mecanica-classica-e-quantica-n-corpos/src/calculos.py:118): `energial_total(...)`
- [src/calculos.py](/Users/joaocrm/Documents/dev/mestrado/mecanica-classica-e-quantica-n-corpos/src/calculos.py:105): `hamiltoniano_total(...)`

### Momento linear total

```text
P = m1 v1 + m2 v2
```

No código:

- [src/calculos.py](/Users/joaocrm/Documents/dev/mestrado/mecanica-classica-e-quantica-n-corpos/src/calculos.py:133): `momento_liner_total(...)`

### Momento angular total

```text
L = r1 x (m1 v1) + r2 x (m2 v2)
```

No código:

- [src/calculos.py](/Users/joaocrm/Documents/dev/mestrado/mecanica-classica-e-quantica-n-corpos/src/calculos.py:136): `momento_angular_total(...)`

## 11. Comparação entre formalismos

Depois de rodar os três formalismos, o projeto compara as trajetórias usando o formalismo newtoniano como referência.

As métricas atuais são:

```text
max |r1_formalismo - r1_newtonian|
max |r2_formalismo - r2_newtonian|
```

No código:

- [src/trabalho_analysis.py](/Users/joaocrm/Documents/dev/mestrado/mecanica-classica-e-quantica-n-corpos/src/trabalho_analysis.py:69): `compare_formalisms(...)`

### Interpretação

Se essas diferenças forem muito pequenas, isso indica que os três formalismos estão descrevendo a mesma dinâmica física no experimento numérico.

## 12. Organização da execução

O fluxo principal é:

1. `main.py` lê um cenário YAML.
2. Roda os três formalismos.
3. Salva um `.npz` por formalismo.
4. Salva um CSV de performance por formalismo.
5. Salva um relatório individual por formalismo.
6. Salva um relatório comparativo entre os formalismos.

No código:

- [main.py](/Users/joaocrm/Documents/dev/mestrado/mecanica-classica-e-quantica-n-corpos/main.py:17)

## 13. Renderização

A renderização não faz parte do benchmark principal.

O fluxo é:

1. `render_results.py` escolhe um formalismo.
2. Lê o `.npz` correspondente.
3. Chama `src.plot`.
4. Gera gráfico estático e animação.

No código:

- [render_results.py](/Users/joaocrm/Documents/dev/mestrado/mecanica-classica-e-quantica-n-corpos/render_results.py:1)
- [src/plot.py](/Users/joaocrm/Documents/dev/mestrado/mecanica-classica-e-quantica-n-corpos/src/plot.py:54)

## 14. Benchmark

Cada formalismo gera seu próprio CSV de performance com:

- tempo total;
- tempo de CPU;
- CPU média;
- pico de memória.

Isso permite comparar custo computacional entre Newton, Lagrange e Hamilton.

Arquivos principais:

- [src/performance_metrics.py](/Users/joaocrm/Documents/dev/mestrado/mecanica-classica-e-quantica-n-corpos/src/performance_metrics.py:1)
- [src/prepare_execution_chart_data.py](/Users/joaocrm/Documents/dev/mestrado/mecanica-classica-e-quantica-n-corpos/src/prepare_execution_chart_data.py:1)
- [execution_metrics.gnuplot](/Users/joaocrm/Documents/dev/mestrado/mecanica-classica-e-quantica-n-corpos/execution_metrics.gnuplot:1)

## 15. Como apresentar

Uma sequência boa para a apresentação é:

1. explicar o problema físico de dois corpos;
2. mostrar a força gravitacional e a suavização `eps`;
3. mostrar como o estado inicial é montado;
4. explicar os três formalismos;
5. mostrar que o solver integra os três separadamente;
6. apresentar conservação de energia, momento linear e momento angular;
7. mostrar a comparação entre trajetórias;
8. fechar com benchmark e animações.

## 16. Mensagem curta para usar na fala

Você pode resumir assim:

> O projeto resolve o problema gravitacional de dois corpos por integração numérica. A mesma física foi organizada em três formalismos, Newton, Lagrange e Hamilton, e depois comparada numericamente por trajetória, conservação e custo computacional. A renderização foi separada do benchmark para que o tempo medido represente o solver, e não o custo do Matplotlib.
