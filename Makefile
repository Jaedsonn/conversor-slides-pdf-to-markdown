.PHONY: converter testar limpar formatar

converter:
	uv run python -m conversor --todos

testar:
	uv run pytest

limpar:
	rm -f md/*.md

formatar:
	uv run black conversor tests
