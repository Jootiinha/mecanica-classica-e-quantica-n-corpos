# Validação da Implementação

## Objetivo

Este documento valida a implementação atual do projeto contra:

- o enunciado de `docs/Trabalho-1.pdf`;
- os materiais de aula em `docs/MCQ-Aula-5.pdf`, `docs/MCQ-Aula-6.pdf` e `docs/MCQ-Aula-7.pdf`;
- o que foi pedido na thread `Medir tempo e uso de recursos`.

## Resumo executivo

A implementação atual está bem alinhada com a parte computacional newtoniana do trabalho e com o pedido de benchmark da thread. O projeto já:

- executa um cenário por vez a partir de YAML;
- resolve numericamente o problema de dois corpos com `solve_ivp`;
- salva resultados físicos em `.npz`;
- mede tempo, CPU e memória em CSV;
- gera gráfico histórico de performance com `gnuplot`;
- separa benchmark da renderização, o que faz sentido para medições de desempenho.

Por outro lado, a entrega ainda não cobre integralmente o trabalho acadêmico. Faltam:

- solução via Mecânica Lagrangiana;
- solução via Mecânica Hamiltoniana;
- comparação explícita entre os três formalismos;
- verificação efetiva das leis de conservação no fluxo principal;
- uso real da velocidade do centro de massa definida nos cenários.

## Base de comparação

### Trabalho 1

O texto extraído de `docs/Trabalho-1.pdf` pede explicitamente:

- resolver o problema de dois corpos pela Mecânica Newtoniana;
- simular computacionalmente dois conjuntos de cenários:
  - massas iguais, próximas e distantes, em repouso e com velocidade;
  - massas diferentes, próximas e distantes, em repouso e com velocidade;
- resolver o mesmo problema com Mecânica Lagrangiana;
- resolver o mesmo problema com Mecânica Hamiltoniana;
- comparar os três formalismos;
- verificar conservação de momento linear, energia total e momento angular;
- repetir o problema com massas variáveis.

### Aulas

Os materiais `docs/MCQ-Aula-6.pdf` e `docs/MCQ-Aula-5.pdf` reforçam os tópicos de:

- Mecânica Newtoniana;
- condições iniciais;
- Equações de Euler-Lagrange;
- formalismo Hamiltoniano;
- leis de conservação.

Isso é compatível com o escopo do `Trabalho-1.pdf`.

### Thread "Medir tempo e uso de recursos"

Pelo histórico fornecido, a thread pediu:

- medir tempo de execução, CPU e memória;
- salvar esse histórico em CSV para comparação entre ajustes;
- gerar gráfico histórico das execuções;
- não contaminar o benchmark com a geração de gráficos e animações.

## Validação por tópico

### 1. Solução newtoniana

Status: `atende`

Evidências:

- [src/simulacao.py](/Users/joaocrm/Documents/dev/mestrado/mecanica-classica-e-quantica-n-corpos/src/simulacao.py:35) usa `solve_ivp` para integrar o sistema no tempo.
- [src/calculos.py](/Users/joaocrm/Documents/dev/mestrado/mecanica-classica-e-quantica-n-corpos/src/calculos.py:26) implementa a equação de dois corpos a partir da interação gravitacional.
- [src/calculos.py](/Users/joaocrm/Documents/dev/mestrado/mecanica-classica-e-quantica-n-corpos/src/calculos.py:51) e [src/calculos.py](/Users/joaocrm/Documents/dev/mestrado/mecanica-classica-e-quantica-n-corpos/src/calculos.py:52) calculam as acelerações gravitacionais de cada corpo.

Justificativa:

O núcleo atual resolve o problema como sistema de EDOs com base na formulação newtoniana. Isso está de acordo com o item 1 do trabalho e com o conteúdo de aula sobre Mecânica Newtoniana e condições iniciais.

### 2. Cobertura dos cenários pedidos

Status: `atende em boa parte`

Evidências:

- [scenarios/scenario_1_equal_close_rest.yaml](/Users/joaocrm/Documents/dev/mestrado/mecanica-classica-e-quantica-n-corpos/scenarios/scenario_1_equal_close_rest.yaml:1) cobre massas iguais, próximas, em repouso.
- [scenarios/scenario_2_different_far_velocity.yaml](/Users/joaocrm/Documents/dev/mestrado/mecanica-classica-e-quantica-n-corpos/scenarios/scenario_2_different_far_velocity.yaml:1) cobre massas diferentes, distantes, com velocidade.
- [scenarios/scenario_7.yaml](/Users/joaocrm/Documents/dev/mestrado/mecanica-classica-e-quantica-n-corpos/scenarios/scenario_7.yaml:15) cobre o caso de massas variáveis.

Justificativa:

Os arquivos de cenário implementam exatamente a estratégia esperada para o trabalho: parametrizar diferentes condições iniciais e executar o mesmo motor numérico. Isso faz sentido com o enunciado e com a abordagem computacional pedida.

Observação:

Não revisei um a um todos os YAMLs no relatório, mas encontrei evidência suficiente de que a estrutura esperada dos grupos de cenário foi criada.

### 3. Massas variáveis

Status: `atende parcialmente`

Evidências:

- [src/simulacao.py](/Users/joaocrm/Documents/dev/mestrado/mecanica-classica-e-quantica-n-corpos/src/simulacao.py:11) valida a presença de `tau1` e `tau2` quando `massa_variavel` está ativa.
- [src/calculos.py](/Users/joaocrm/Documents/dev/mestrado/mecanica-classica-e-quantica-n-corpos/src/calculos.py:10) define `massa_no_tempo`.
- [src/calculos.py](/Users/joaocrm/Documents/dev/mestrado/mecanica-classica-e-quantica-n-corpos/src/calculos.py:17) implementa decaimento exponencial de massa.
- [scenarios/scenario_7.yaml](/Users/joaocrm/Documents/dev/mestrado/mecanica-classica-e-quantica-n-corpos/scenarios/scenario_7.yaml:15) já ativa esse modo.

Justificativa:

O projeto contempla o item 7 do trabalho em termos de modelagem computacional. O que ainda falta é análise mais explícita desses resultados no relatório ou no fluxo de verificação.

### 4. Geração de gráficos e vídeos

Status: `atende`

Evidências:

- [render_results.py](/Users/joaocrm/Documents/dev/mestrado/mecanica-classica-e-quantica-n-corpos/render_results.py:11) lê os resultados físicos já salvos.
- [src/plot.py](/Users/joaocrm/Documents/dev/mestrado/mecanica-classica-e-quantica-n-corpos/src/plot.py:54) concentra a renderização dos artefatos.
- [src/plot.py](/Users/joaocrm/Documents/dev/mestrado/mecanica-classica-e-quantica-n-corpos/src/plot.py:100) monta a animação.
- [src/plot.py](/Users/joaocrm/Documents/dev/mestrado/mecanica-classica-e-quantica-n-corpos/src/plot.py:197) exporta `mp4` ou `gif`.

Justificativa:

O trabalho pede pequenos vídeos com a evolução do sistema. O projeto já atende essa necessidade.

### 5. Benchmark separado da renderização

Status: `atende e faz sentido com a thread`

Evidências:

- [main.py](/Users/joaocrm/Documents/dev/mestrado/mecanica-classica-e-quantica-n-corpos/main.py:18) executa a simulação e salva apenas os resultados físicos.
- [main.py](/Users/joaocrm/Documents/dev/mestrado/mecanica-classica-e-quantica-n-corpos/main.py:34) registra as métricas depois da simulação principal.
- [render_results.py](/Users/joaocrm/Documents/dev/mestrado/mecanica-classica-e-quantica-n-corpos/render_results.py:22) renderiza em um fluxo separado.
- [Makefile](/Users/joaocrm/Documents/dev/mestrado/mecanica-classica-e-quantica-n-corpos/Makefile:26) mantém `run-adhoc` para benchmark.
- [Makefile](/Users/joaocrm/Documents/dev/mestrado/mecanica-classica-e-quantica-n-corpos/Makefile:30) mantém `render` separado.

Justificativa:

Essa separação atende diretamente ao que foi pedido na thread: medir desempenho sem misturar custo do Matplotlib, Pillow ou ffmpeg com o custo do solver numérico.

### 6. Persistência de métricas em CSV

Status: `atende`

Evidências:

- [src/performance_metrics.py](/Users/joaocrm/Documents/dev/mestrado/mecanica-classica-e-quantica-n-corpos/src/performance_metrics.py:14) define o schema do CSV com timestamp, `run_label`, tempo, CPU e memória.
- [src/performance_metrics.py](/Users/joaocrm/Documents/dev/mestrado/mecanica-classica-e-quantica-n-corpos/src/performance_metrics.py:49) calcula as métricas ao final da execução.
- [src/performance_metrics.py](/Users/joaocrm/Documents/dev/mestrado/mecanica-classica-e-quantica-n-corpos/src/performance_metrics.py:66) anexa cada nova medição ao CSV.

Justificativa:

Isso está alinhado com o pedido da thread para acompanhar evolução de performance ao longo das otimizações.

### 7. Gráfico histórico das execuções

Status: `atende`

Evidências:

- [src/prepare_execution_chart_data.py](/Users/joaocrm/Documents/dev/mestrado/mecanica-classica-e-quantica-n-corpos/src/prepare_execution_chart_data.py:31) ordena as execuções por `timestamp_utc`.
- [src/prepare_execution_chart_data.py](/Users/joaocrm/Documents/dev/mestrado/mecanica-classica-e-quantica-n-corpos/src/prepare_execution_chart_data.py:10) usa `run_label` no eixo x quando disponível.
- [Makefile](/Users/joaocrm/Documents/dev/mestrado/mecanica-classica-e-quantica-n-corpos/Makefile:48) gera o gráfico com `gnuplot`.

Justificativa:

Isso também atende ao que foi pedido na thread: acompanhar a evolução das medições da execução mais antiga para a mais nova.

## Lacunas relevantes

### 1. Mecânica Lagrangiana não está implementada

Status: `não atende`

Evidências:

- [src/simulacao.py](/Users/joaocrm/Documents/dev/mestrado/mecanica-classica-e-quantica-n-corpos/src/simulacao.py:35) resolve apenas o sistema com `solve_ivp` sobre a equação newtoniana.
- Não encontrei evidência no projeto de um módulo, solver ou relatório que implemente Equações de Euler-Lagrange.

Impacto:

O item 3 do `Trabalho-1.pdf` não está coberto.

### 2. Mecânica Hamiltoniana não está implementada

Status: `não atende`

Evidências:

- Não encontrei evidência no projeto de um módulo, solver ou relatório que implemente Equações de Hamilton.
- O fluxo atual depende apenas de [src/calculos.py](/Users/joaocrm/Documents/dev/mestrado/mecanica-classica-e-quantica-n-corpos/src/calculos.py:26) e [src/simulacao.py](/Users/joaocrm/Documents/dev/mestrado/mecanica-classica-e-quantica-n-corpos/src/simulacao.py:35), ambos centrados na formulação newtoniana.

Impacto:

O item 4 do `Trabalho-1.pdf` não está coberto.

### 3. Comparação entre os três formalismos não existe

Status: `não atende`

Evidências:

- Não encontrei evidência no projeto de comparação entre Newton, Lagrange e Hamilton.

Impacto:

O item 5 do `Trabalho-1.pdf` também fica descoberto.

### 4. Leis de conservação estão implementadas como funções auxiliares, mas não são verificadas no fluxo

Status: `atende parcialmente`

Evidências:

- [src/calculos.py](/Users/joaocrm/Documents/dev/mestrado/mecanica-classica-e-quantica-n-corpos/src/calculos.py:61) define energia total.
- [src/calculos.py](/Users/joaocrm/Documents/dev/mestrado/mecanica-classica-e-quantica-n-corpos/src/calculos.py:76) define momento linear total.
- [src/calculos.py](/Users/joaocrm/Documents/dev/mestrado/mecanica-classica-e-quantica-n-corpos/src/calculos.py:79) define momento angular total.
- A busca por uso dessas funções retornou apenas as próprias definições.

Impacto:

O item 6 do `Trabalho-1.pdf` não está completo, porque as grandezas existem no código, mas não há evidência de cálculo sistemático, relatório ou validação automática.

### 5. `center_mass_velocity` existe nos cenários, mas hoje não influencia a simulação

Status: `não atende ao contrato implícito do YAML`

Evidências:

- [scenarios/scenario_1_equal_close_rest.yaml](/Users/joaocrm/Documents/dev/mestrado/mecanica-classica-e-quantica-n-corpos/scenarios/scenario_1_equal_close_rest.yaml:14), [scenarios/scenario_2_different_far_velocity.yaml](/Users/joaocrm/Documents/dev/mestrado/mecanica-classica-e-quantica-n-corpos/scenarios/scenario_2_different_far_velocity.yaml:14) e [scenarios/scenario_7.yaml](/Users/joaocrm/Documents/dev/mestrado/mecanica-classica-e-quantica-n-corpos/scenarios/scenario_7.yaml:14) definem `center_mass_velocity`.
- [src/simulacao.py](/Users/joaocrm/Documents/dev/mestrado/mecanica-classica-e-quantica-n-corpos/src/simulacao.py:23) ignora o valor do YAML e fixa `center_mass_velocity = [0.0, 0.0, 0.0]`.

Impacto:

Os cenários expressam uma intenção física que não está sendo respeitada pela implementação atual.

### 6. Não existe a flag `CHART` pedida depois na thread

Status: `não atende ao pedido mais recente da thread`

Evidências:

- [main.py](/Users/joaocrm/Documents/dev/mestrado/mecanica-classica-e-quantica-n-corpos/main.py:27) finaliza a medição e encerra a execução sem qualquer leitura de `CHART`.
- A busca no código não encontrou `CHART`.

Impacto:

Hoje a separação benchmark/render está correta, mas o fluxo alternativo pedido na thread, de renderizar no final do `main` condicionado por flag, ainda não foi implementado.

### 7. Adimensionalização não está explicada explicitamente

Status: `indício parcial`

Evidências:

- Os cenários usam `gravity: 1.0` e escalas numéricas normalizadas, como em [scenarios/scenario_1_equal_close_rest.yaml](/Users/joaocrm/Documents/dev/mestrado/mecanica-classica-e-quantica-n-corpos/scenarios/scenario_1_equal_close_rest.yaml:4).

Justificativa:

Há indícios de uso de unidades adimensionais, o que faz sentido com a recomendação do trabalho. Porém, não encontrei evidência suficiente no projeto para afirmar que a adimensionalização foi formalmente documentada ou demonstrada.

## Conclusão

### Decisão

Considero que a implementação atual está consistente com:

- a parte computacional newtoniana do trabalho;
- a geração de cenários e vídeos;
- a necessidade de benchmark, CSV histórico e gráfico pedida na thread;
- a separação correta entre benchmark e renderização.

### Evidência

- solver newtoniano em [src/simulacao.py](/Users/joaocrm/Documents/dev/mestrado/mecanica-classica-e-quantica-n-corpos/src/simulacao.py:35);
- força gravitacional em [src/calculos.py](/Users/joaocrm/Documents/dev/mestrado/mecanica-classica-e-quantica-n-corpos/src/calculos.py:26);
- CSV de métricas em [src/performance_metrics.py](/Users/joaocrm/Documents/dev/mestrado/mecanica-classica-e-quantica-n-corpos/src/performance_metrics.py:14);
- benchmark separado da renderização em [main.py](/Users/joaocrm/Documents/dev/mestrado/mecanica-classica-e-quantica-n-corpos/main.py:18) e [render_results.py](/Users/joaocrm/Documents/dev/mestrado/mecanica-classica-e-quantica-n-corpos/render_results.py:11).

### Alternativa considerada

A alternativa seria considerar que o projeto já atende integralmente ao trabalho porque os cenários e vídeos existem. Essa interpretação não se sustenta, porque os itens de Lagrange, Hamilton e verificação efetiva das leis de conservação não aparecem implementados.

### Risco

O principal risco acadêmico é apresentar a solução como se cobrisse todo o `Trabalho-1.pdf`, quando hoje ela cobre com clareza apenas a parte newtoniana, os cenários e a infraestrutura computacional de benchmark/render.

## Próximos passos recomendados

1. Corrigir o uso de `center_mass_velocity` em [src/simulacao.py](/Users/joaocrm/Documents/dev/mestrado/mecanica-classica-e-quantica-n-corpos/src/simulacao.py:23).
2. Adicionar um fluxo explícito de verificação de energia, momento linear e momento angular usando as funções já existentes em [src/calculos.py](/Users/joaocrm/Documents/dev/mestrado/mecanica-classica-e-quantica-n-corpos/src/calculos.py:61).
3. Decidir se o trabalho será ampliado para contemplar Lagrange e Hamilton no código, ou se isso ficará restrito à parte teórica da apresentação.
4. Implementar a flag `CHART` em `main.py` apenas se você quiser reaproximar benchmark e render em um único entrypoint opcional.
