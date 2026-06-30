# Principais Funções da Simulação

## Função principal

### `simular_dois_corpos_3d(...)`

Arquivo: `src/simulacao.py`

Essa é a função central do projeto. Ela:

- prepara o estado inicial;
- chama o integrador numérico;
- organiza a solução final;
- devolve posições, velocidades, momentos e centro de massa.

## Funções físicas mais importantes

### `equacao_newton_dois_corpos(...)`

Arquivo: `src/calculos.py`

É a função que define a dinâmica do sistema. Ela transforma o estado atual nas derivadas que o integrador precisa usar.

### `aceleracoes_gravitacionais(...)`

Arquivo: `src/calculos.py`

Calcula a interação gravitacional entre os dois corpos.

### `massa_no_tempo(...)`

Arquivo: `src/calculos.py`

Controla se a massa permanece constante ou varia exponencialmente no tempo.

## Funções de apoio físico

### `posicao_centro_massa(...)`

Calcula a posição do centro de massa.

### `velocidade_centro_massa(...)`

Calcula a velocidade do centro de massa.

### `energial_total(...)`, `momento_liner_total(...)`, `momento_angular_total(...)`

Calculam grandezas globais úteis para interpretar a simulação.

## Funções de visualização

### `render_simulation_artifacts(...)`

Arquivo: `src/plot.py`

Coordena a geração de gráfico estático e animação.

### `build_animated_plot(...)`

Arquivo: `app.py`

Monta a animação 3D interativa usada no protótipo web.

## Funções de execução

### `run_simulation()`

Arquivo: `main.py`

É a entrada da execução no terminal. Carrega o cenário, chama a simulação e salva os resultados.

### `append_metrics_csv(...)`

Arquivo: `src/performance_metrics.py`

Grava no CSV os dados de desempenho de cada execução.

## Resumo para falar

> A função principal é `simular_dois_corpos_3d`. Ela depende da função física `equacao_newton_dois_corpos`, que calcula a dinâmica do sistema, e depois entrega os resultados para as camadas de visualização e análise.
