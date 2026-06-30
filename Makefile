.PHONY: clean run render render-all install help execution_chart web

FORMALISM ?= newtonian

help:
	@echo "Comandos disponíveis:"
	@echo "  make install  - Instala as dependências do projeto com poetry"
	@echo "  make run      - Executa todos os cenarios YAML e salva os resultados do solver newtoniano"
	@echo "  make run-adhoc SCENARIO=arquivo.yaml RUN_LABEL=nome - Executa um cenario e salva benchmark"
	@echo "  make render SCENARIO=arquivo.yaml FORMALISM=newtonian - Gera graficos e animacao do formalismo newtoniano"
	@echo "  make render-all - Renderiza todos os cenarios com resultados .npz do formalismo newtoniano"
	@echo "  make execution_chart FORMALISM=newtonian - Gera um grafico PNG do historico do formalismo"
	@echo "  make web      - Inicia o prototipo Streamlit para explorar parametros interativamente"
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
	@$(MAKE) execution_chart FORMALISM="$(FORMALISM)"

run-adhoc:
	mkdir -p outputs/.mpl-cache
	PYTHONDONTWRITEBYTECODE=1 MPLCONFIGDIR=outputs/.mpl-cache MPLBACKEND=Agg RUN_LABEL="$(RUN_LABEL)" SCENARIO="$(SCENARIO)" poetry run python -m main

render:
	mkdir -p outputs/.mpl-cache
	PYTHONDONTWRITEBYTECODE=1 MPLCONFIGDIR=outputs/.mpl-cache MPLBACKEND=Agg SCENARIO="$(SCENARIO)" FORMALISM="$(FORMALISM)" poetry run python -m render_results

render-all:
	mkdir -p outputs/.mpl-cache
	@for scenario in scenarios/*.yaml; do \
		filename="$${scenario##*/}"; \
		stem="$${filename%.yaml}"; \
		results_file="outputs/formalisms/$(FORMALISM)/results/$${stem}.npz"; \
		if [ -f "$$results_file" ]; then \
			echo "Renderizando $$filename [$(FORMALISM)]"; \
			PYTHONDONTWRITEBYTECODE=1 MPLCONFIGDIR=outputs/.mpl-cache MPLBACKEND=Agg SCENARIO="$$filename" FORMALISM="$(FORMALISM)" poetry run python -m render_results; \
		else \
			echo "Pulando $$filename [$(FORMALISM)] (resultado ausente: $$results_file)"; \
		fi; \
	done

execution_chart:
	@test -f outputs/formalisms/$(FORMALISM)/performance_metrics.csv || (echo "Arquivo outputs/formalisms/$(FORMALISM)/performance_metrics.csv nao encontrado."; exit 1)
	@command -v gnuplot >/dev/null 2>&1 || (echo "gnuplot nao encontrado no PATH."; exit 1)
	@mkdir -p outputs/formalisms/$(FORMALISM)/charts
	@FORMALISM="$(FORMALISM)" poetry run python -m src.prepare_execution_chart_data
	@gnuplot -e "datafile='outputs/formalisms/$(FORMALISM)/charts/execution_metrics_plot_data.tsv'; outfile='outputs/formalisms/$(FORMALISM)/charts/execution_metrics.png'" execution_metrics.gnuplot
	@echo "Grafico gerado em outputs/formalisms/$(FORMALISM)/charts/execution_metrics.png"

web:
	poetry run streamlit run app.py

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	@echo "Limpeza concluída!"
