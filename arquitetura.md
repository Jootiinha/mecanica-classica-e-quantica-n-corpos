# Arquitetura

## Visão geral

```mermaid
flowchart TD
    A[Cenario YAML] --> B[main.py]
    B --> C[Simulacao por formalismo]
    C --> D[Resultados por formalismo]
    C --> E[Metricas por formalismo]
    C --> F[Relatorios do trabalho]

    D --> G[render_results.py]
    G --> H[Graficos e animacoes]

    E --> I[prepare_execution_chart_data.py]
    I --> J[Grafico de performance]
```

## Papéis dos módulos

- `main.py`: executa o mesmo cenário nos formalismos `newtonian`, `lagrangian` e `hamiltonian`.
- `src/simulacao.py`: monta o estado inicial e integra o sistema com `solve_ivp`.
- `src/calculos.py`: concentra as equações físicas, energia, momento linear e momento angular.
- `src/trabalho_analysis.py`: compara formalismos e gera os relatórios do trabalho.
- `src/performance_metrics.py`: mede tempo, CPU e memória e salva um CSV por formalismo.
- `render_results.py`: lê o `.npz` de um formalismo e delega a renderização.
- `src/plot.py`: gera gráfico estático e animação.
- `src/prepare_execution_chart_data.py` + `execution_metrics.gnuplot`: transformam o CSV em gráfico histórico de benchmark.
- `src/utils.py`: centraliza carga de YAML e caminhos de saída em `outputs/`.
