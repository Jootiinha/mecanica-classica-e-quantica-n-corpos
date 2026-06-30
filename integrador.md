# Como funciona a integração com DOP853

O `DOP853` é um método numérico para resolver EDOs passo a passo no tempo. Ele pertence à família **Runge-Kutta explícita** e foi projetado para oferecer **alta ordem de precisão**.

## Ideia geral

Queremos resolver um sistema do tipo:

```text
y'(t) = f(t, y)
y(t0) = y0
```

No projeto, `y` representa o estado do sistema:

- posições;
- velocidades;
- ou momentos, dependendo do formalismo.

O `DOP853` parte do estado inicial `y0` e calcula aproximações sucessivas:

1. pega o estado atual;
2. avalia a derivada `f(t, y)` várias vezes dentro do intervalo;
3. combina essas avaliações;
4. estima o próximo estado.

## O significado do nome

- `DO` vem de **Dormand-Prince**;
- `8` indica solução principal de **ordem 8**;
- `5` e `3` vêm de fórmulas embutidas de erro usadas no controle adaptativo.

Na prática, isso significa que o método:

- calcula uma solução muito precisa;
- estima o erro local a cada passo.

## Como o passo é escolhido

O método não depende de passo fixo.

A lógica é:

1. tenta avançar um passo `h`;
2. calcula uma aproximação de alta ordem;
3. estima o erro desse passo;
4. compara com as tolerâncias (`rtol`, `atol`);
5. se o erro estiver alto, reduz `h`;
6. se o erro estiver baixo, pode aumentar `h`.

Isso torna o método **adaptativo**:

- regiões mais difíceis usam passos menores;
- regiões mais suaves usam passos maiores.

## O que ele calcula em cada passo

Em métodos Runge-Kutta, o integrador calcula vários pontos intermediários dentro do mesmo passo.

De forma simplificada:

```text
k1 = f(t, y)
k2 = f(t + a2*h, y + combinação de k1)
k3 = f(t + a3*h, y + combinação de k1, k2)
...
```

Depois, o método combina esses valores para obter o próximo estado.

No `DOP853`, isso é feito com várias avaliações por passo para atingir ordem alta.

## Aplicação no problema de dois corpos

No problema de dois corpos:

- o estado atual contém posição e velocidade;
- a função `f` calcula as derivadas;
- essas derivadas vêm da força gravitacional e das equações do movimento.

Assim, o integrador repete:

1. lê posição e velocidade atuais;
2. calcula a aceleração gravitacional;
3. monta as derivadas do sistema;
4. avança no tempo com controle de erro.

## Como isso aparece no código

No projeto, isso ocorre em `src/simulacao.py`:

```python
solver_object = solve_ivp(
    _solver_function(formalism),
    [0.0, caso['physics']['t_final']],
    init_parameters,
    t_eval=time_span,
    args=(...),
    method='DOP853',
    rtol=1e-10,
    atol=1e-10
)
```

Os pontos principais são:

- `_solver_function(formalism)`: função que define as EDOs;
- `[0.0, t_final]`: intervalo de tempo;
- `init_parameters`: estado inicial;
- `t_eval=time_span`: pontos onde a solução será avaliada;
- `method='DOP853'`: integrador utilizado;
- `rtol` e `atol`: tolerâncias de erro numérico.

## Intuição curta

Uma forma simples de resumir:

> O DOP853 constrói a solução da EDO avançando no tempo e recalculando a inclinação do sistema várias vezes dentro de cada passo. Ele ajusta automaticamente o tamanho do passo para manter o erro pequeno.

## Texto curto para slide

```md
O método DOP853 resolve numericamente as equações diferenciais do movimento passo a passo no tempo. Em cada passo, ele avalia várias vezes a derivada do sistema, estima o erro local e ajusta automaticamente o tamanho do passo para manter alta precisão.
```

## Justificativas baseadas na natureza do cálculo

### A implementação newtoniana teve execução muito rápida, na ordem de milissegundos

O problema resolvido é pequeno do ponto de vista computacional: são apenas dois corpos em 3D, com um estado de baixa dimensão. No formalismo newtoniano, a cada passo o código calcula posições, velocidades e acelerações usando operações algébricas diretas sobre vetores curtos. Não há malhas, grandes matrizes, nem interação entre muitos corpos. Isso reduz bastante o custo por passo de integração.

### O processo utilizou praticamente um núcleo completo durante a integração numérica

A integração temporal é essencialmente sequencial: o estado no instante seguinte depende do estado anterior. Por isso, o método numérico não se paraleliza de forma natural nessa implementação. O trabalho dominante fica concentrado em avaliar repetidamente a função das equações diferenciais, o que caracteriza uma carga principalmente de CPU.

### O consumo de memória permaneceu estável, próximo de 100 MB

O algoritmo não precisa manter estruturas grandes em memória. Ele trabalha basicamente com:

- vetores de estado pequenos;
- séries temporais das posições, velocidades e momento;
- alguns arrays auxiliares do solver.

Como o número de corpos é fixo e pequeno, a memória cresce principalmente com o número de pontos salvos no tempo, e não com estruturas complexas ou dados volumosos.

### Isso indica uma implementação computacional leve em memória e intensiva em CPU durante o cálculo

O comportamento esperado desse tipo de solução é exatamente esse:

- leve em memória, porque o problema tem baixa dimensão e usa poucas estruturas de dados;
- intensivo em CPU, porque a maior parte do custo está na integração numérica e nas sucessivas avaliações das equações do movimento.


Versão curta:
    Escolhi o DOP853 porque ele oferece alta precisão para EDOs não rígidas e funciona bem para trajetórias suaves como as do problema gravitacional de dois corpos.
Versão boa para apresentação:
    O DOP853 foi escolhido porque o problema simulado é não rígido, de baixa dimensão e exige boa precisão na evolução temporal das trajetórias.
    Como é um método de ordem alta, ele consegue manter erro pequeno com poucos passos efetivos.
    Além disso, o controle adaptativo do passo ajuda a ajustar automaticamente o esforço numérico ao longo da simulação.