# Validação da Implementação

## Objetivo

Este documento valida a implementação atual do projeto contra:

- o enunciado de `docs/Trabalho-1.pdf`;
- os materiais de aula em `docs/MCQ-Aula-5.pdf`, `docs/MCQ-Aula-6.pdf` e `docs/MCQ-Aula-7.pdf`;
- o pedido de benchmark e renderização separado já incorporado ao repositório.

## Resumo executivo

A implementação atual está consistente com um recorte computacional newtoniano do problema de dois corpos. O projeto hoje:

- executa cenários YAML com um solver newtoniano;
- salva resultados físicos em `.npz`;
- calcula energia, momento linear e momento angular no relatório da execução;
- mede tempo, CPU e memória em CSV;
- gera gráfico histórico de performance com `gnuplot`;
- separa benchmark da renderização.

O escopo atual é explícito: o repositório foi reduzido para o fluxo newtoniano e não tenta mais manter caminhos alternativos de execução.

## Base de comparação

### Trabalho 1

O enunciado pede uma solução computacional do problema de dois corpos, com cenários variados, análise física e materiais para apresentação.

### Aulas

Os materiais de aula reforçam:

- Mecânica Newtoniana;
- condições iniciais;
- integração numérica;
- leis de conservação.

Isso é compatível com o núcleo implementado no projeto.

## Validação por tópico

### 1. Solução numérica do problema de dois corpos

Status: `atende`

Evidências:

- [src/simulacao.py](/Users/joaocrm/Documents/dev/mestrado/mecanica-classica-e-quantica-n-corpos/src/simulacao.py:50) integra o sistema com `solve_ivp`.
- [src/calculos.py](/Users/joaocrm/Documents/dev/mestrado/mecanica-classica-e-quantica-n-corpos/src/calculos.py:32) define a equação diferencial de primeira ordem.
- [src/calculos.py](/Users/joaocrm/Documents/dev/mestrado/mecanica-classica-e-quantica-n-corpos/src/calculos.py:24) calcula as acelerações gravitacionais.

Justificativa:

O núcleo do projeto resolve o problema como sistema de EDOs de primeira ordem a partir da formulação newtoniana.

### 2. Cobertura de cenários

Status: `atende`

Evidências:

- [scenarios/scenario_1_equal_close_rest.yaml](/Users/joaocrm/Documents/dev/mestrado/mecanica-classica-e-quantica-n-corpos/scenarios/scenario_1_equal_close_rest.yaml:1)
- [scenarios/scenario_2_unequal_far_velocity.yaml](/Users/joaocrm/Documents/dev/mestrado/mecanica-classica-e-quantica-n-corpos/scenarios/scenario_2_unequal_far_velocity.yaml:1)
- [scenarios/scenario_7_equal_asymmetric_mass_loss.yaml](/Users/joaocrm/Documents/dev/mestrado/mecanica-classica-e-quantica-n-corpos/scenarios/scenario_7_equal_asymmetric_mass_loss.yaml:1)

Justificativa:

O diretório `scenarios/` cobre combinações de massas, distância inicial, repouso, velocidade inicial e casos com massa variável.

### 3. Massa variável

Status: `atende`

Evidências:

- [src/simulacao.py](/Users/joaocrm/Documents/dev/mestrado/mecanica-classica-e-quantica-n-corpos/src/simulacao.py:54) valida `tau1` e `tau2` quando `massa_variavel` está ativa.
- [src/calculos.py](/Users/joaocrm/Documents/dev/mestrado/mecanica-classica-e-quantica-n-corpos/src/calculos.py:12) implementa `massa_no_tempo(...)`.
- [scenarios/scenario_7_equal_asymmetric_mass_loss.yaml](/Users/joaocrm/Documents/dev/mestrado/mecanica-classica-e-quantica-n-corpos/scenarios/scenario_7_equal_asymmetric_mass_loss.yaml:1) ativa esse modo.

Justificativa:

O projeto implementa o caso de massa dependente do tempo e o propaga pelo solver e pelos relatórios.

### 4. Velocidade do centro de massa

Status: `atende`

Evidências:

- [src/simulacao.py](/Users/joaocrm/Documents/dev/mestrado/mecanica-classica-e-quantica-n-corpos/src/simulacao.py:25) lê `center_mass_velocity` do cenário.
- [src/simulacao.py](/Users/joaocrm/Documents/dev/mestrado/mecanica-classica-e-quantica-n-corpos/src/simulacao.py:27) e [src/simulacao.py](/Users/joaocrm/Documents/dev/mestrado/mecanica-classica-e-quantica-n-corpos/src/simulacao.py:28) somam essa velocidade às velocidades iniciais.

Justificativa:

O contrato físico expresso nos YAMLs é respeitado pelo estado inicial do solver.

### 5. Leis de conservação

Status: `atende`

Evidências:

- [src/calculos.py](/Users/joaocrm/Documents/dev/mestrado/mecanica-classica-e-quantica-n-corpos/src/calculos.py:73) calcula energia total.
- [src/calculos.py](/Users/joaocrm/Documents/dev/mestrado/mecanica-classica-e-quantica-n-corpos/src/calculos.py:87) calcula momento linear total.
- [src/calculos.py](/Users/joaocrm/Documents/dev/mestrado/mecanica-classica-e-quantica-n-corpos/src/calculos.py:90) calcula momento angular total.
- [src/analysis.py](/Users/joaocrm/Documents/dev/mestrado/mecanica-classica-e-quantica-n-corpos/src/analysis.py:25) resume os desvios relativos máximos.
- [main.py](/Users/joaocrm/Documents/dev/mestrado/mecanica-classica-e-quantica-n-corpos/main.py:35) gera o relatório da execução.

Justificativa:

As grandezas físicas não ficam mais só como funções auxiliares; elas entram no relatório salvo a cada execução.

### 6. Benchmark separado da renderização

Status: `atende`

Evidências:

- [main.py](/Users/joaocrm/Documents/dev/mestrado/mecanica-classica-e-quantica-n-corpos/main.py:24) executa a simulação e salva apenas resultados e métricas.
- [render_results.py](/Users/joaocrm/Documents/dev/mestrado/mecanica-classica-e-quantica-n-corpos/render_results.py:18) renderiza a partir de resultados previamente salvos.
- [Makefile](/Users/joaocrm/Documents/dev/mestrado/mecanica-classica-e-quantica-n-corpos/Makefile:17) mantém `run` separado de [Makefile](/Users/joaocrm/Documents/dev/mestrado/mecanica-classica-e-quantica-n-corpos/Makefile:32) `render`.

Justificativa:

Essa separação mantém o benchmark focado no solver e evita misturar custo de Matplotlib, Pillow ou ffmpeg com o custo da integração numérica.

### 7. Persistência de métricas e gráfico histórico

Status: `atende`

Evidências:

- [src/performance_metrics.py](/Users/joaocrm/Documents/dev/mestrado/mecanica-classica-e-quantica-n-corpos/src/performance_metrics.py:14) define o schema de métricas.
- [src/performance_metrics.py](/Users/joaocrm/Documents/dev/mestrado/mecanica-classica-e-quantica-n-corpos/src/performance_metrics.py:66) anexa novas medições ao CSV.
- [src/prepare_execution_chart_data.py](/Users/joaocrm/Documents/dev/mestrado/mecanica-classica-e-quantica-n-corpos/src/prepare_execution_chart_data.py:20) transforma o CSV em dados para gráfico.
- [Makefile](/Users/joaocrm/Documents/dev/mestrado/mecanica-classica-e-quantica-n-corpos/Makefile:46) gera o PNG histórico com `gnuplot`.

Justificativa:

O projeto preserva o histórico de execuções e mantém um fluxo reprodutível para análise de desempenho.

### 8. Gráficos e vídeos

Status: `atende`

Evidências:

- [render_results.py](/Users/joaocrm/Documents/dev/mestrado/mecanica-classica-e-quantica-n-corpos/render_results.py:28) delega a renderização a `src.plot`.
- [src/plot.py](/Users/joaocrm/Documents/dev/mestrado/mecanica-classica-e-quantica-n-corpos/src/plot.py:55) gera gráfico estático e animação.
- [src/plot.py](/Users/joaocrm/Documents/dev/mestrado/mecanica-classica-e-quantica-n-corpos/src/plot.py:165) faz fallback para Pillow quando `ffmpeg` não está disponível.

Justificativa:

O fluxo de renderização gera os artefatos visuais necessários sem contaminar a medição principal.

## Conclusão

### Decisão

Considero que a implementação atual está coerente com o escopo que o repositório assumiu: resolver, medir e renderizar o problema de dois corpos no formalismo newtoniano.

### Evidência

- solver em [src/simulacao.py](/Users/joaocrm/Documents/dev/mestrado/mecanica-classica-e-quantica-n-corpos/src/simulacao.py:50);
- dinâmica em [src/calculos.py](/Users/joaocrm/Documents/dev/mestrado/mecanica-classica-e-quantica-n-corpos/src/calculos.py:32);
- relatório físico em [src/analysis.py](/Users/joaocrm/Documents/dev/mestrado/mecanica-classica-e-quantica-n-corpos/src/analysis.py:61);
- benchmark em [src/performance_metrics.py](/Users/joaocrm/Documents/dev/mestrado/mecanica-classica-e-quantica-n-corpos/src/performance_metrics.py:14);
- renderização separada em [render_results.py](/Users/joaocrm/Documents/dev/mestrado/mecanica-classica-e-quantica-n-corpos/render_results.py:18).

### Risco

O principal risco agora é acadêmico e de comunicação: apresentar esse repositório como se cobrisse mais do que o fluxo newtoniano realmente implementado.

## Próximos passos recomendados

1. Manter a documentação alinhada ao escopo newtoniano do código.
2. Usar `main.py` para benchmark e `render_results.py` para geração de artefatos visuais.
3. Se o trabalho acadêmico exigir escopo maior no futuro, tratar isso como uma expansão nova, não como compatibilidade legada.
