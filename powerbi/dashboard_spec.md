# Especificação do dashboard

Formato: 16:9, 1440 × 810. Grade de 12 colunas, margens externas de 24 px e espaçamento de 16 px.

## Página 1 — Visão executiva

**Objetivo:** responder em menos de 30 segundos se o negócio está crescendo com rentabilidade.

- Cabeçalho: título, período selecionado e data da última atualização.
- Filtros: período, região e canal.
- Cards: Receita Líquida, Crescimento YoY, Margem %, Pedidos e Ticket Médio.
- Linha: receita mensal atual versus ano anterior, com anotação do maior desvio.
- Bullet chart: receita realizada versus meta de +10% sobre o ano anterior.
- Barras horizontais: margem por categoria, ordenada do maior para o menor.
- Caixa de insight: texto curto com principal oportunidade ou risco.

## Página 2 — Comercial

**Objetivo:** localizar os produtos, canais e regiões que explicam o resultado.

- Barras horizontais: ranking de produtos por Receita Líquida.
- Matriz: categoria → produto, com receita, margem, unidades e participação.
- Small multiples: tendência mensal por canal, usando a mesma escala.
- Dispersão: Receita Líquida × Margem %, tamanho por unidades, rótulo para outliers.
- Tooltip dedicado com preço, desconto, margem e participação.

## Página 3 — Clientes

**Objetivo:** acompanhar aquisição, retenção e valor da base.

- Cards: Clientes Ativos, Clientes Recorrentes, Taxa de Recompra e Ticket Médio.
- Heatmap de coortes: mês da primeira compra × meses desde aquisição.
- Linha: novos versus recorrentes ao longo do tempo, com estilos diferentes além da cor.
- Barras: Receita Líquida por segmento.
- Tabela: segmentos por estado, com formatação condicional acessível.

## Página 4 — Estoque

**Objetivo:** priorizar reposição e reduzir ruptura ou excesso.

- Cards: Estoque Disponível, Produtos para Reposição e valor estimado imobilizado.
- Barras: produtos com menor cobertura em dias.
- Matriz: loja × categoria com estoque e ponto de reposição.
- Tabela operacional: produto, loja, saldo, cobertura, lead time e status.
- Drill-through de produto com histórico de vendas e estoque.

## Interações

- Seleções cruzadas devem filtrar, não apenas realçar, quando a análise exigir decomposição.
- Botão “Limpar filtros” em todas as páginas.
- Navegação por botões com texto e ícone.
- Drill-through somente onde adiciona contexto.
- Tooltips devem complementar, nunca esconder a métrica principal.

## Acessibilidade

- Contraste mínimo AA.
- Fonte mínima de 11 pt nos elementos analíticos.
- Ordem de tabulação definida.
- Alt text com o principal achado de cada visual.
- Azul e laranja como par principal; status também recebe texto ou ícone.
- Barras partem de zero; escalas de small multiples permanecem iguais.
- Disponibilizar tabela alternativa para coortes e gráficos principais.
