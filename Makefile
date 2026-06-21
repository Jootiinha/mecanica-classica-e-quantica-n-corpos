.PHONY: clean run install help execution_chart

help:
	@echo "Comandos disponíveis:"
	@echo "  make install  - Instala as dependências do projeto com poetry"
	@echo "  make run      - Executa a aplicação com poetry sem gerar __pycache__"
	@echo "  make run-adhoc RUN_LABEL=nome - Executa a simulacao adhoc e salva o nome no CSV"
	@echo "  make execution_chart - Gera um grafico PNG com o historico de execucoes"
	@echo "  make clean    - Remove arquivos __pycache__ e .pyc"
	@echo "  make help     - Mostra esta mensagem"

install:
	poetry install

run-adhoc:
	mkdir -p outputs/.mpl-cache
	PYTHONDONTWRITEBYTECODE=1 MPLCONFIGDIR=outputs/.mpl-cache MPLBACKEND=Agg RUN_LABEL="$(RUN_LABEL)" poetry run python -m main

execution_chart:
	@test -f outputs/performance_metrics.csv || (echo "Arquivo outputs/performance_metrics.csv nao encontrado."; exit 1)
	@command -v gnuplot >/dev/null 2>&1 || (echo "gnuplot nao encontrado no PATH."; exit 1)
	@mkdir -p outputs/charts
	@poetry run python src/prepare_execution_chart_data.py
	@gnuplot -e "datafile='outputs/charts/execution_metrics_plot_data.tsv'; outfile='outputs/charts/execution_metrics.png'" execution_metrics.gnuplot
	@echo "Grafico gerado em outputs/charts/execution_metrics.png"

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	@echo "Limpeza concluída!"
