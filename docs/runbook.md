# Runbook operacional

## Objetivo

Restaurar a ingestão e a camada analítica com segurança, preservando evidências e evitando publicação parcial.

## Verificação diária

1. Consultar `raw.vw_pipeline_health` e confirmar `status = succeeded`.
2. Verificar duração, volume e taxa de rejeição contra a execução anterior.
3. Consultar `raw.vw_data_freshness` e confirmar atualização das sete fontes.
4. Executar a reconciliação financeira.
5. Investigar novas regras em `raw.vw_rejections_by_rule`.

## Incidente: banco indisponível

- Confirmar health check do container.
- Verificar porta e variáveis de conexão sem exibir a senha nos logs.
- Permitir as tentativas automáticas.
- Se a indisponibilidade persistir, interromper novas cargas e preservar os arquivos recebidos.
- Retomar com a mesma entrada; a idempotência evita duplicação.

## Incidente: aumento de rejeições

- Comparar regras e fontes afetadas com a execução anterior.
- Não remover regras para fazer a carga “passar”.
- Confirmar se houve mudança legítima no contrato da fonte.
- Corrigir ou versionar o contrato e reprocessar somente após aprovação.

## Incidente: reconciliação diferente de zero

- Suspender atualização do dashboard.
- Comparar contagens entre staging e marts.
- Verificar filtros de status e joins com dimensões.
- Corrigir a transformação e reexecutar a transação dos marts.
- Registrar causa, impacto e prevenção.

## Rollback

As cargas em staging são transacionais. Para mudanças de código, reverta o commit responsável e execute novamente a partir dos registros preservados em raw. Não apague a camada raw durante a recuperação.

## Critérios de escalonamento

- Dados financeiros incorretos publicados: prioridade alta.
- Perda ou exposição de dados: crítica e imediata.
- Falha sem impacto no consumo: média.
- Rejeição esperada documentada: baixa.
