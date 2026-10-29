# Dicionário de KPIs

| KPI | Definição inicial | Granularidade | Observação |
|---|---|---|---|
| Receita bruta | Soma de quantidade × preço unitário antes de descontos | Pedido/item | Não inclui cancelamentos concluídos |
| Desconto | Soma dos descontos aplicados aos itens | Pedido/item | Sempre armazenado como valor não negativo |
| Receita líquida | Receita bruta − descontos − devoluções | Pedido/item | Impostos não serão descontados na primeira versão |
| Custo dos produtos | Soma de quantidade × custo unitário | Pedido/item | Custo registrado no momento da venda |
| Margem bruta | Receita líquida − custo dos produtos | Pedido/item | Pode ser negativa |
| Margem percentual | Margem bruta ÷ receita líquida | Período/segmento | Nula quando a receita líquida for zero |
| Pedidos | Contagem distinta de pedidos válidos | Período | Pedidos cancelados serão separados |
| Ticket médio | Receita líquida ÷ pedidos válidos | Período/segmento | Requer contagem distinta de pedidos |
| Clientes ativos | Clientes distintos com compra válida | Período | O período deve ser informado no relatório |
| Taxa de recompra | Clientes com duas ou mais compras ÷ clientes compradores | Coorte/período | A janela deve ser explícita |
| Cobertura de estoque | Estoque disponível ÷ média diária de vendas | Produto/local | Usará janela móvel configurável |
| Risco de ruptura | Cobertura inferior ao lead time estimado | Produto/local | Indicador operacional, não previsão definitiva |

## Regras

- Todo KPI exibido no dashboard deve apontar para uma definição deste documento.
- Mudanças de regra devem ser registradas e versionadas.
- Métricas financeiras devem declarar tratamento de cancelamentos, devoluções, impostos e descontos.
