.PHONY: clean run install help

help:
	@echo "Comandos disponíveis:"
	@echo "  make install  - Instala as dependências do projeto com poetry"
	@echo "  make run      - Executa a aplicação com poetry sem gerar __pycache__"
	@echo "  make clean    - Remove arquivos __pycache__ e .pyc"
	@echo "  make help     - Mostra esta mensagem"

install:
	poetry install

run-adhoc:
	PYTHONDONTWRITEBYTECODE=1 poetry run python simulacao_adhoc/main.py

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	@echo "Limpeza concluída!"
