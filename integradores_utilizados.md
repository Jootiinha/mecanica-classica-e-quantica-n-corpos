# Integradores Utilizados

## Integrador usado no projeto

O código atual usa um integrador numérico:

- `DOP853`, via `scipy.integrate.solve_ivp`

Ele é chamado em `src/simulacao.py`.

## O que ele faz

O integrador recebe a equação diferencial do sistema e calcula, passo a passo, a evolução das posições e velocidades dos dois corpos.

Em outras palavras, ele transforma o modelo matemático em trajetória numérica.

## Como isso entra no código

O solver trabalha sobre um vetor de estado:

`w = [r1, r2, v1, v2]`

e a função física devolve:

`dw/dt = [v1, v2, a1, a2]`

Isso quer dizer:

- posição deriva em velocidade;
- velocidade deriva em aceleração gravitacional.

## Por que esse integrador é adequado aqui

No código atual, o `DOP853` é usado com tolerâncias bem rígidas:

- `rtol = 1e-10`
- `atol = 1e-10`

Isso é útil porque o projeto quer trajetórias numéricas estáveis para:

- análise física;
- geração de gráficos;
- geração de animações;
- exploração no protótipo web.

## Relação com massa variável

Mesmo quando a massa muda no tempo, o integrador continua sendo o mesmo.

O que muda é a equação física avaliada a cada instante, porque `massa_no_tempo(...)` altera `m1(t)` e `m2(t)`.

## Resumo para falar

> O projeto usa o método DOP853 para integrar numericamente a dinâmica dos dois corpos. A física é reescrita como um sistema de primeira ordem, e o integrador calcula a trajetória com alta precisão ao longo do tempo.
