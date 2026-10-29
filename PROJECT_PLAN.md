# Plano de execução

Este arquivo serve como ponto de continuidade entre as etapas do projeto.

## Estratégia

Cada fase deve resultar em uma entrega executável ou verificável. O projeto não dependerá de etapas futuras para explicar o valor das etapas já concluídas.

## Fase 1 — Fundação

- [x] Definir problema de negócio
- [x] Selecionar stack inicial
- [x] Definir arquitetura evolutiva
- [x] Definir indicadores principais
- [x] Criar estrutura do repositório
- [x] Registrar critérios de qualidade

## Fase 2 — Dados sintéticos

- [x] Definir esquema lógico das fontes
- [x] Criar gerador determinístico de dados
- [x] Incluir sazonalidade, promoções e comportamento de recompra
- [x] Incluir problemas controlados de qualidade
- [x] Gerar amostra pequena versionável
- [x] Criar dicionário de dados
- [x] Testar reprodutibilidade

## Fase 3 — Banco e ingestão

- [x] Criar PostgreSQL local com Docker
- [x] Criar schemas `raw`, `staging` e `marts`
- [x] Implementar carga inicial e incremental
- [x] Garantir idempotência
- [x] Registrar logs e rejeições

> A infraestrutura e a ingestão foram implementadas e validadas em modo seco. O teste de
> integração com PostgreSQL aguarda a disponibilidade do Docker no ambiente local.

## Fase 4 — Modelagem e SQL

- [x] Criar dimensões de data, cliente, produto, loja e canal
- [x] Criar fatos de vendas e estoque
- [x] Implementar chaves substitutas
- [x] Implementar histórico de dimensões quando aplicável
- [x] Criar consultas analíticas e validações de reconciliação

> O modelo e os contratos SQL foram validados estaticamente. A execução integrada aguarda
> a disponibilidade do Docker/PostgreSQL no ambiente local.

## Fase 5 — Pipeline e qualidade

- [x] Organizar o código Python em módulos
- [x] Criar testes unitários e contratos de integração
- [x] Validar unicidade, integridade, domínio e completude
- [x] Criar relatório de qualidade
- [x] Definir comportamento de retry e falha

> Os testes unitários e de contrato estão ativos. O teste integrado real com PostgreSQL
> permanece condicionado à instalação do Docker.

## Fase 6 — BI

- [x] Construir especificação do modelo semântico
- [x] Criar catálogo de medidas DAX
- [x] Criar visão executiva e prévia renderizada
- [x] Especificar páginas comercial, clientes e estoque
- [x] Documentar decisões, acessibilidade e recomendações

> A especificação está pronta para implementação. A criação do arquivo `.pbix` requer
> Power BI Desktop, que não está disponível no ambiente atual.

## Fase 7 — Engenharia de produção

- [x] Empacotar ambiente com Docker Compose
- [x] Configurar validações, testes e GitHub Actions
- [x] Adicionar health checks e métricas
- [x] Criar runbook e registro de decisões arquiteturais
- [x] Revisar segurança, dependências e segredos

> A integração PostgreSQL será executada automaticamente no GitHub Actions. Localmente,
> continua dependendo da instalação do Docker.

## Fase 8 — Publicação

- [x] Revisar README para recrutadores
- [x] Criar imagem de demonstração
- [x] Adicionar resultados e aprendizados
- [ ] Publicar repositório no GitHub
- [ ] Fixar projeto no perfil

## Critério de conclusão

O projeto estará concluído quando uma pessoa puder cloná-lo, subir o ambiente, gerar ou carregar os dados, executar o pipeline, rodar os testes e visualizar os resultados seguindo apenas o README.
