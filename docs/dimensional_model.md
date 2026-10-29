# Modelo dimensional

## Processos e granularidade

| Tabela fato | Granularidade | Dimensões principais |
|---|---|---|
| fact_sales | Uma linha por item de pedido | Data, cliente, produto, loja, canal e promoção |
| fact_inventory_snapshot | Um produto por loja por data de fotografia | Data, produto e loja |

## Estratégia das dimensões

- `dim_date`: calendário compartilhado por todos os fatos.
- `dim_customer`: SCD Tipo 2 para preservar mudanças de cidade, estado, segmento e consentimento.
- `dim_product`: SCD Tipo 1; correções substituem os atributos atuais.
- `dim_store`: SCD Tipo 1.
- `dim_channel`: domínio pequeno e estável.
- `dim_promotion`: cadastro de campanhas.

Todas as dimensões usam chaves substitutas. As chaves naturais permanecem disponíveis para rastreabilidade e integração.

## Medidas aditivas

Na fato de vendas, receita bruta, desconto, receita líquida, custo e margem são materializados na granularidade do item. Percentuais e ticket médio devem ser calculados somente após agregação, evitando médias de médias.

## Tratamento de status

A fato preserva pedidos concluídos, cancelados e devolvidos. As visões executivas filtram `Completed`; análises específicas podem mensurar cancelamentos e devoluções separadamente.

## Histórico de cliente

Uma alteração detectada pelo hash encerra a versão corrente e cria outra. O vínculo da venda utiliza a versão válida na data do pedido, preservando a interpretação histórica.
