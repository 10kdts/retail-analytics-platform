# Segurança e privacidade

## Controles implementados

- Dados exclusivamente sintéticos.
- `.env` ignorado pelo Git; somente `.env.example` é versionado.
- Segredos de CI definidos como variáveis efêmeras do serviço.
- Dependabot para dependências Python e GitHub Actions.
- CodeQL para análise estática.
- Permissões mínimas declaradas nos workflows.
- RLS documentado para consumo regional no Power BI.
- Payloads e logs não devem conter credenciais.

## Antes de publicar

- Executar busca por tokens, senhas e arquivos `.env`.
- Confirmar que e-mails usam somente `example.com`.
- Revisar permissões dos workflows.
- Fixar versões principais de Actions confiáveis.
- Habilitar proteção da branch principal e revisão de PR.
- Habilitar secret scanning e alertas de dependência no GitHub.

## Ameaças consideradas

| Ameaça | Mitigação |
|---|---|
| Credencial versionada | `.gitignore`, exemplo sem segredo real e secret scanning |
| SQL injection | Queries parametrizadas na ingestão |
| Publicação parcial | Transações e rollback |
| Duplicação em reprocessamento | Hash e restrição de unicidade |
| Acesso regional indevido | RLS e permissões de workspace |
| Dependência vulnerável | Dependabot e CodeQL |
