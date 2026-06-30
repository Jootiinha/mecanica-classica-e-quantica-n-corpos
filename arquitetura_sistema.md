# Arquitetura do Sistema

## Ideia central

O projeto foi organizado para separar bem três responsabilidades:

- definir o cenário;
- resolver a física;
- visualizar o resultado.

Essa separação evita misturar equações, interface e geração de arquivos no mesmo lugar.

## Fluxo do sistema

O fluxo principal é este:

`scenarios/*.yaml` -> `main.py` -> `src/simulacao.py` -> `src/calculos.py`

Depois da simulação, o sistema salva:

- resultados numéricos em `.npz`
- métricas de execução em `.csv`

Se o objetivo for gerar figuras ou animações, o fluxo continua por:

`render_results.py` -> `src/plot.py`

Se o objetivo for exploração interativa, o fluxo vai por:

`app.py` -> `src/simulacao.py`

## Papel de cada parte

### `main.py`

É o orquestrador. Carrega o cenário, roda a simulação e salva os resultados.

### `src/simulacao.py`

É o núcleo da execução numérica. Monta o estado inicial, chama o integrador e reorganiza a solução.

### `src/calculos.py`

É onde está a física. Aqui ficam as equações do problema, as massas no tempo e as grandezas derivadas.

### `src/plot.py`

É a camada de visualização offline. Gera gráfico estático e animação.

### `app.py`

É a camada interativa. Reaproveita o mesmo solver e mostra a trajetória em 3D com Plotly.

## Ponto forte da arquitetura

O principal acerto do sistema é que a física está concentrada em `src/simulacao.py` e `src/calculos.py`.

Isso permite:

- reutilizar o mesmo solver no terminal e na interface web;
- trocar a visualização sem reescrever a modelagem física;
- explicar o sistema de forma mais limpa na apresentação.

## Resumo para falar

> A arquitetura é simples: o YAML define o experimento, o núcleo numérico resolve a dinâmica e as camadas de visualização reutilizam esse resultado para gerar gráficos, animações e interface interativa.
