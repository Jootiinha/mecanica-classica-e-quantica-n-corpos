# Simulação de Interação Gravitacional de 2 Corpos

Este projeto implementa simulações gravitacionais configuradas por arquivos YAML, com foco em experimentos de dois corpos, cenários com massas iguais ou diferentes, e casos com massa variável. O software separa a definição dos cenários, o motor físico e a geração de artefatos visuais.

---

## 🛠️ Pré-Requisitos e Instalação

1. Clone o repositório para a sua máquina local.
2. Certifique-se de ter o Python 3.13+ e o Poetry instalados.
3. Abra o terminal na raiz do projeto e execute os comandos abaixo:

### 1. Instalar as dependências
```bash
poetry install
```

### 2. Executar um cenário específico
```bash
SCENARIO=scenario_7.yaml poetry run python -m main
```

### 3. Gerar animações
```bash
poetry run python src/create_animations.py
```

### Alternativa com Makefile
```bash
make install
make run
make run-adhoc SCENARIO=scenario_7_unequal_star_moderate_mass_loss.yaml RUN_LABEL=baseline
make web
```

## Execução

### Rodar todos os cenários

O alvo abaixo percorre todos os arquivos `*.yaml` dentro de `scenarios/`, executa um por vez e registra as métricas em `outputs/performance_metrics.csv` usando o nome do arquivo como `run_label`.

```bash
make run
```

### Rodar um cenário específico

Use `run-adhoc` quando quiser executar só um arquivo YAML e definir um identificador explícito para comparação de performance.

```bash
make run-adhoc SCENARIO=scenario_7_unequal_star_moderate_mass_loss.yaml RUN_LABEL=teste_otimizacao
```

### Rodar o protótipo web

O protótipo web usa `Streamlit` para a interface e `Plotly` para a visualização 3D interativa. Ele reaproveita o solver atual e permite alterar parâmetros, recalcular a órbita e inspecionar um instante específico da trajetória.

```bash
make web
```

ou:

```bash
poetry run streamlit run app.py
```

### Gerar gráfico das execuções

```bash
make execution_chart
```

O gráfico é salvo em `outputs/charts/execution_metrics.png`.

## 🚀 Funcionalidades

- **Configuração Dinâmica:** Cada experimento é definido por um arquivo YAML em `scenarios/`.
- **Motor Físico Otimizado:** Cálculos baseados na Lei da Gravitação Universal de Newton 
- **Renderização Eficiente:** Geração de animações `.gif` via Matplotlib 
- **Execução em Lote:** Capacidade de simular múltiplos cenários sequencialmente com `make run`.
- **Medição de Performance:** Registro de tempo, CPU e memória em CSV e geração de gráfico histórico com `gnuplot`.

---

## 📂 Estrutura do Projeto

O projeto adota uma estrutura modular para garantir que os dados brutos da física não poluam o código-fonte ou os arquivos de mídia gerados:

```text
MECANICA-CLASSICA-E-QUANTICA-N-CORPOS/
│
├── scenarios/                    # Cenários de entrada em YAML
├── src/                          # Código fonte do projeto
│   ├── simulacao.py              # Motor físico principal
│   ├── performance_metrics.py    # Coleta e persistência de métricas
│   └── create_animations.py      # Renderizador de gráficos e animações
│
├── main.py                       # Orquestrador da execução por cenário
├── pyproject.toml                # Dependências e configuração do Poetry
│
├── outputs/                      # Arquivos gerados pela execução
│
└── .venv/                        # Ambiente virtual gerado pelo Poetry
