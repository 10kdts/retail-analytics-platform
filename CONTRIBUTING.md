# Contribuindo

## Ambiente

1. Crie um ambiente virtual com Python 3.10 ou superior.
2. Instale o projeto com `pip install -e .`.
3. Gere a base com `python -m src.retail_data.generate`.
4. Execute `python -m unittest discover -s tests -v`.

## Mudanças

- Preserve a granularidade documentada das tabelas fato.
- Atualize o dicionário quando alterar campos ou regras.
- Adicione testes para novas regras de qualidade.
- Não versione credenciais, dados pessoais ou arquivos `.env`.
- Registre decisões arquiteturais relevantes em `docs/adr/`.

## Pull requests

Explique o problema, a decisão adotada, como a mudança foi validada e possíveis impactos em dados ou indicadores.
