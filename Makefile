.PHONY: clean run render render-all install help execution_chart

FORMALISM ?= newtonian
FORMALISMS := newtonian lagrangian hamiltonian

help:
	@echo "Comandos disponíveis:"
	@echo "  make install  - Instala as dependências do projeto com poetry"
	@echo "  make run      - Executa todos os cenarios YAML, salva os resultados fisicos e gera os graficos de performance dos 3 formalismos"
	@echo "  make run-adhoc SCENARIO=arquivo.yaml RUN_LABEL=nome - Executa um cenario e salva benchmark"
	@echo "  make render SCENARIO=arquivo.yaml FORMALISM=hamiltonian - Gera graficos e animacao do formalismo escolhido"
	@echo "  make render-all - Renderiza todos os cenarios com resultados .npz disponiveis para todos os formalismos"
	@echo "  make execution_chart FORMALISM=newtonian - Gera um grafico PNG do historico do formalismo"
	@echo "  make clean    - Remove arquivos __pycache__ e .pyc"
	@echo "  make help     - Mostra esta mensagem"

install:
	poetry install

run:
	mkdir -p outputs/.mpl-cache
	@for scenario in scenarios/*.yaml; do \
		filename="$${scenario##*/}"; \
		label="$${filename%.yaml}"; \
		echo "Executando $$filename"; \
		PYTHONDONTWRITEBYTECODE=1 MPLCONFIGDIR=outputs/.mpl-cache MPLBACKEND=Agg RUN_LABEL="$$label" SCENARIO="$$filename" poetry run python -m main; \
	done
	@for formalism in $(FORMALISMS); do \
		$(MAKE) execution_chart FORMALISM="$$formalism"; \
	done

run-adhoc:
	mkdir -p outputs/.mpl-cache
	PYTHONDONTWRITEBYTECODE=1 MPLCONFIGDIR=outputs/.mpl-cache MPLBACKEND=Agg RUN_LABEL="$(RUN_LABEL)" SCENARIO="$(SCENARIO)" poetry run python -m main

render:
	mkdir -p outputs/.mpl-cache
	PYTHONDONTWRITEBYTECODE=1 MPLCONFIGDIR=outputs/.mpl-cache MPLBACKEND=Agg SCENARIO="$(SCENARIO)" FORMALISM="$(FORMALISM)" poetry run python -m render_results

render-all:
	mkdir -p outputs/.mpl-cache
	@for formalism in $(FORMALISMS); do \
		for scenario in scenarios/*.yaml; do \
			filename="$${scenario##*/}"; \
			stem="$${filename%.yaml}"; \
			results_file="outputs/formalisms/$$formalism/results/$${stem}.npz"; \
			if [ -f "$$results_file" ]; then \
				echo "Renderizando $$filename [$${formalism}]"; \
				PYTHONDONTWRITEBYTECODE=1 MPLCONFIGDIR=outputs/.mpl-cache MPLBACKEND=Agg SCENARIO="$$filename" FORMALISM="$$formalism" poetry run python -m render_results; \
			else \
				echo "Pulando $$filename [$${formalism}] (resultado ausente: $$results_file)"; \
			fi; \
		done; \
	done

execution_chart:
	@test -f outputs/formalisms/$(FORMALISM)/performance_metrics.csv || (echo "Arquivo outputs/formalisms/$(FORMALISM)/performance_metrics.csv nao encontrado."; exit 1)
	@command -v gnuplot >/dev/null 2>&1 || (echo "gnuplot nao encontrado no PATH."; exit 1)
	@mkdir -p outputs/formalisms/$(FORMALISM)/charts
	@FORMALISM="$(FORMALISM)" poetry run python -m src.prepare_execution_chart_data
	@gnuplot -e "datafile='outputs/formalisms/$(FORMALISM)/charts/execution_metrics_plot_data.tsv'; outfile='outputs/formalisms/$(FORMALISM)/charts/execution_metrics.png'" execution_metrics.gnuplot
	@echo "Grafico gerado em outputs/formalisms/$(FORMALISM)/charts/execution_metrics.png"

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	@echo "Limpeza concluída!"
