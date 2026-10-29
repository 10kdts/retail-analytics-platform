# Arquitetura

## Princípios

1. **Reprodutibilidade:** os dados sintéticos e resultados podem ser recriados.
2. **Idempotência:** reexecutar uma carga não duplica registros.
3. **Rastreabilidade:** cada execução registra origem, horário e resultado.
4. **Qualidade por padrão:** dados inválidos são identificados antes do consumo.
5. **Separação de responsabilidades:** ingestão, transformação e apresentação permanecem desacopladas.
6. **Evolução gradual:** a solução começa localmente e pode migrar para cloud sem redesenho completo.

## Camadas

### Fontes

Arquivos CSV sintéticos representarão inicialmente sistemas de vendas, cadastro e estoque. Uma API simulada poderá ser adicionada posteriormente.

### Raw

Preserva a estrutura recebida e acrescenta metadados de ingestão. Não contém regras analíticas.

### Staging

Normaliza tipos, nomes, datas, valores ausentes, duplicidades e códigos de negócio.

### Marts

Disponibiliza fatos e dimensões modelados para consumo analítico e Power BI.

### Consumo

O Power BI utilizará o modelo dimensional e medidas explícitas. Análises Python poderão consumir as mesmas tabelas certificadas.

## Evolução para nível especialista

Após a versão local, o projeto poderá receber orquestração, catálogo, lineage, políticas de acesso, testes de contrato, monitoramento de freshness e uma implantação equivalente em cloud.
