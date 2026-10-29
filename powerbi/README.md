# Implementação no Power BI

## Ordem recomendada

1. Conectar ao PostgreSQL e importar as tabelas `marts.dim_*` e `marts.fact_*`.
2. Criar os relacionamentos descritos em `semantic_model.md`.
3. Marcar `dim_date` como tabela de datas usando `full_date`.
4. Ocultar chaves técnicas e colunas usadas apenas para relacionamento.
5. Criar uma tabela vazia `_Measures` e copiar `measures.dax`.
6. Importar `theme.json` em **Exibir → Temas → Procurar temas**.
7. Montar as quatro páginas conforme `dashboard_spec.md`.
8. Configurar a regra de segurança descrita em `rls.md`.
9. Executar o checklist de acessibilidade antes da publicação.

## Atualização

Use modo Import para o portfólio local. Em um cenário corporativo, a escolha entre Import, DirectQuery e modelo composto deve considerar volumetria, latência, capacidade e requisitos de segurança.
