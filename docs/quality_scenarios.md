# Cenários controlados de qualidade

A base padrão contém cinco falhas intencionais. Elas permitem demonstrar detecção, quarentena, correção e métricas de qualidade sem depender de dados pessoais ou de problemas acidentais.

| Regra | Cenário | Tratamento esperado na ingestão |
|---|---|---|
| state_not_null | Cliente sem UF | Rejeitar ou enviar à quarentena |
| email_unique | Dois clientes com o mesmo e-mail | Sinalizar duplicidade para revisão |
| valid_channel | Pedido com canal fora do domínio | Rejeitar e registrar valor recebido |
| quantity_positive | Item com quantidade negativa | Rejeitar linha e impedir impacto financeiro |
| order_fk | Item ligado a pedido inexistente | Rejeitar até a chegada/correção do pai |

O arquivo `expected_quality_issues.csv` identifica as linhas afetadas. Na Fase 5 ele funcionará como uma espécie de gabarito: a suíte de qualidade deverá encontrar exatamente essas ocorrências.

Use `--clean` no gerador quando for necessário produzir uma versão sem anomalias.
