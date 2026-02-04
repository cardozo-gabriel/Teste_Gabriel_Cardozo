# Teste Estágio IntuitiveCare 2026

## Tecnologias
- Python 3.13.2

## Dependências

Este projeto utiliza bibliotecas externas para a comunicação web e processamento de dados:
    - requests: realizada para requisições HTTP.
    - beautifulsoup4: utilizada para extração de dados HTML (scraping).
    - pandas: utilizada para a manipulação, filtragem e normalização das tabelas.

**Instalação:** pip install requests beautifulsoup4 pandas openpyxl 
-------------------------------------------------------------------------------------------

## Como executar
    1 - Criar ambiente virtual

    2 - Instalar dependências

    3 - Executar main.py (O script realiza o download, extração e tratamento dos dados)

## Passo a passo para execução (Backend)

**Configuração do Banco de Dados**

Antes de iniciar a API, certifique-se de que o banco de dados PostgreSQL está rodando e configurado:

*Criação do Banco:* Crie um banco de dados chamado ans_db.

*Credenciais:* Abra o arquivo api/database.py e insira a sua senha do PostgreSQL no campo password.

1. Abra o arquivo `sql/import.sql`.
2. Substitua o texto `'C:/CAMINHO_PARA_O_PROJETO/...'` pelo caminho absoluto da pasta onde você descompactou este teste em sua máquina.
3. Certifique-se de que o usuário do banco de dados tem permissão de leitura na referida pasta.

*Carga de Dados:* Execute os scripts contidos na pasta /sql (schema.sql e import.sql) para preparar as tabelas e dados
    
*1 - Instalação de dependências:* 

        pip install fastapi uvicorn psycopg2

*2 - Inicialização do Servidor:* 
    - No terminal, dentro da pasta do projeto, execute: `uvicorn api.main:app --reload` (sem as aspas)

*3 - Documentação Interativa:* Com o servidor rodando, a documentação completa pode ser acessada em: http://127.0.0.1:8000/docs

## Passo a passo para execução (Frontend):

    Para rodar a interface web, siga os comandos abaixo na pasta do projeto:

*1 - Entrar no diretório:* cd frontend

*2 - Instalação de dependências:* npm install

*3 - Instalação das bibliotecas de comunicação e gráficos:* npm install axios chart.js vue-chartjs
    
`Nota: O axios é utilizado para o consumo da API, enquanto chart.js e vue-chartjs gerenciam a visualização das estatísticas financeiras`

*4 - Inicialização do servidor de desenvolvimento:* npm run dev

*Acesso local:* O sistema estará disponível em: http://localhost:5173/


ficou assim meu readme na parte de como executar, o que achou?

----------------------- **Camada de Banco de Dados (Parte 3)** -----------------------

### Instruções para Importação de Dados
Devido às restrições de segurança do comando `COPY` no PostgreSQL, que exige caminhos absolutos para leitura de arquivos, os scripts de importação utilizam um marcador de posição.

**Para reproduzir o ambiente:**
1. Abra o arquivo `sql/import.sql`.
2. Substitua o texto `'C:/CAMINHO_PARA_O_PROJETO/...'` pelo caminho absoluto da pasta onde você descompactou este teste em sua máquina.
3. Certifique-se de que o usuário do banco de dados tem permissão de leitura na referida pasta.

-----------------------------------------------------------------------------------------------
## Estrutura do projeto

A arquitetura do projeto foi organizada em módulos independentes para garantir escalabilidade e facilitar a manutenção de cada camada do sistema (Dados, Backend e Frontend).

*1. /api (Backend)/*
Contém o servidor de aplicação desenvolvido em FastAPI.

`main.py:` Ponto de entrada da API, contendo a definição das rotas e lógica de busca/paginação.

`database.py:` Módulo de conexão com o banco de dados PostgreSQL.

__pycache__: Arquivos de cache do Python (gerados automaticamente).

*2. /data (Camada de Dados)*

Armazena o ciclo de vida dos dados utilizados no projeto.

`/raw:` Arquivos CSV originais obtidos da ANS.

`/processed:` Dados limpos e validados após a primeira etapa de tratamento.

`/output:` Arquivos finais prontos para a carga no banco de dados (DML).

*3. /frontend (Interface Web)*

Projeto desenvolvido em Vue.js 3 utilizando Vite como build tool.

`/src/components:` Componentes reutilizáveis:

`OperadorasTable.vue:` Tabela interativa com paginação.

`EstatisticasChart.vue:` Gráficos gerados com Chart.js.

`OperadoraDetalhes.vue:` Modal de histórico financeiro.

`App.vue:` Componente principal que orquestra o estado e as chamadas de API.

`package.json:` Gerenciador de dependências e scripts do Node.js.

*4. /sql (Persistência)*

Scripts para configuração e manipulação do banco de dados relacional.

`schema.sql:` Definição das tabelas e chaves primárias/estrangeiras (DDL).

`import.sql:` Comandos COPY para carga de alto volume de dados (DML).

`queries.sql:` Consultas de validação e análises ad-hoc.

*5. /src (Pipeline de ETL)*

Scripts Python responsáveis pelo processamento pesado dos dados.

`ans_client.py:` Lógica de web scraping ou coleta de dados.

`enricher.py:` Processo de Join e limpeza de CNPJs.

`processor.py:` Agregações estatísticas e cálculos financeiros.

`requirements.txt:` Dependências necessárias para rodar o pipeline de dados.

*6. Arquivos de Raiz*

`.gitignore:` Define arquivos que não devem ser versionados (ex: node_modules, venv).

`README.md:` Guia principal com decisões técnicas e instruções de execução.

`main.py:` Script mestre para execução do pipeline completo de dados.

## Decisões técnicas (Trade-offs)

    - Descoberta dinâmica de trimestres: O bot navega pelo repositório da ANS para encontrar os 3 períodos mais recentes, garantindo que o código não quebre com a virada do ano.

    - Processamento Incremental: Optei por processar um arquivo por vez em vez de carregar tudo na memória. Isso garante escalabilidade para lidar com o grande volume de dados das demonstrações contábeis.

     - Agregação por Soma: Decidi somar os valores das contas contábeis por operadora antes de remover duplicatas, garantindo que o ValorDespesas final represente o gasto total real do trimestre.

**Transformação e Validação de Dados (Parte 2)**

Nesta etapa, foquei na qualidade e no enriquecimento da base financeira com dados cadastrais da ANS.

* **Estratégia de Validação de CNPJ (Parte 2.1):**
    * **Abordagem:** Realizei a limpeza de caracteres e apliquei o algoritmo de dígitos verificadores da Receita Federal. 
    * **Trade-off:** Decidi **descartar** registros com CNPJs inválidos. 
    * **Justificativa:** Em análises financeiras e regulatórias, dados atribuídos a identificadores inexistentes são considerados "ruído" e podem comprometer a credibilidade de relatórios gerenciais e agregações por estado.

* **Processamento do Join e Enriquecimento (Parte 2.2):**
    * **Estratégia:** Utilizei o `Registro ANS` como chave primária para buscar o `CNPJ`, `UF` e `Modalidade` no Relatório de Operadoras Ativas.
    * **Tratamento de Falhas (Match):** Identifiquei que algumas operadoras presentes no financeiro (Ex: Registro 477) não constam no cadastro de ativas.
    * **Decisão:** Optei por **ignorar** esses registros no arquivo final enriquecido.
    * **Justificativa:** Para cumprir os requisitos de validação de CNPJ e as futuras agregações por UF, o match cadastral é obrigatório. Registros órfãos impossibilitariam o enriquecimento dos campos exigidos no desafio.

* **Resiliência na Coleta de Dados:**
    * Implementei uma busca dinâmica na pasta de dados abertos da ANS para localizar o arquivo `Relatorio_cadop.csv`. Isso evita que o pipeline quebre caso o nome do arquivo seja alterado no servidor (ex: inclusão de datas no nome).

* **Estratégia de Processamento do Join (Parte 2.2):**
   
    * **Abordagem:** Processamento em memória utilizando a biblioteca Pandas (`merge`).
    * **Justificativa Baseada no Volume de Dados:** * Estimei o volume de dados em aproximadamente 1.200 registros no cadastro de operadoras e cerca de 500 a 600 registros no consolidado financeiro após a limpeza inicial.
        * Para este volume (KBs ou poucos MBs), o processamento **em memória** oferece a melhor performance, com tempo de execução quase instantâneo e código de alta legibilidade.
        * **Análise de Escalabilidade:** Caso o volume de dados fosse na ordem de dezenas de milhões de registros (Big Data), a estratégia ideal seria o processamento distribuído (ex: PySpark) ou o uso de um banco de dados relacional com índices otimizados, evitando o estouro da memória RAM.

* **Estratégia de Ordenação (Parte 2.3):**
    * **Abordagem:** Utilizei o método `sort_values` do Pandas (que implementa internamente o algoritmo *Quicksort* ou *Mergesort*).
    * **Justificativa:** * **Volume de Dados:** Como o dataset agregado contém algumas centenas de linhas (uma por operadora/UF), a ordenação em memória é extremamente rápida e consome recursos negligenciáveis da CPU.
        * **Recursos Disponíveis:** O ambiente de execução padrão de scripts Python lida facilmente com a complexidade $O(N \log N)$ para este volume de dados.
        * **Alternativa de Escalabilidade:** Se estivéssemos lidando com bilhões de registros, a ordenação deveria ser feita via Banco de Dados (cláusula `ORDER BY` com índices) ou através de partições em sistemas de processamento distribuído para evitar o gargalo de um único núcleo de processamento.

* **3.2 Modelagem de Dados e Trade-offs**

    Normalização: Optei pela Opção B (Tabelas Normalizadas) para garantir a integridade referencial. Em um cenário com milhões de linhas (volume esperado da ANS), a desnormalização causaria um inchaço desnecessário do banco.

    Precisão Monetária: O uso de DECIMAL(18,2) foi mandatório para evitar a perda de centavos em operações de agregação (Soma/Média), problema comum ao utilizar o tipo FLOAT.

    Performance: Criei índices nas colunas cnpj (para buscas rápidas de operadoras) e no par ano/trimestre (para otimizar as queries analíticas de crescimento temporal)

* **Desenvolvimento de API e Integração (Parte 4.2)**
    
    Nesta etapa, implementei um servidor de  para disponibilizar os dados processados para o ecossistema web.

    **Escolha do Framework (Parte 4.2.1):**

    **Opção Escolhida:** FastAPI.

    **Justificativa:** Optei pelo FastAPI em detrimento do Flask devido à sua performance superior (baseado em Starlette e Pydantic) e suporte nativo a operações assíncronas. Além disso, a geração automática de documentação interativa (Swagger UI) acelerou o ciclo de testes e garante que a API seja autodocumentada para outros desenvolvedores.

    **Estratégia de Paginação (Parte 4.2.2):**

    **Abordagem:** Offset-based (LIMIT e OFFSET). 

    **Justificativa:** Considerando que o volume de dados de operadoras da ANS é moderado (algumas milhares de linhas) e a frequência de atualizações/inserções é trimestral (baixa volatilidade), a paginação por offset oferece a melhor relação entre simplicidade de implementação e eficiência de navegação. Abordagens como cursor-based seriam excessivamente complexas para este cenário de uso.

    **Cache vs Queries Diretas (Parte 4.2.3):**

    **Abordagem:** Opção C (Pré-calcular e armazenar em tabela).

    **Justificativa:** Como os dados financeiros da ANS são estáticos após o processamento trimestral, não há necessidade de cálculos computacionais pesados a cada requisição. Ao consumir a tabela despesas_agregadas (criada na Parte 2.3/3.2), a API entrega respostas em milissegundos, garantindo consistência total entre a interface web e os relatórios gerados no banco de dados.

    **Estrutura de Resposta da API (Parte 4.2.4):**

    **Abordagem:** Opção B (Dados + Metadados).

    **Justificativa:** Retornar os dados encapsulados com metadados (como total, page e limit) é uma boa prática de design de API. Esta estrutura fornece ao Frontend (Vue.js) todas as informações necessárias para renderizar componentes de paginação de forma dinâmica, sem a necessidade de chamadas adicionais para contar o volume total de registros.


    **Interface Web e Experiência do Usuário (Parte 4.3)**
    
    Desenvolvi uma interface reativa utilizando Vue.js 3 para visualização e busca dos dados das operadoras.

    **Trade-offs técnicos - Frontend:**

    *Visualização de Dados (Gráficos) - Item 4.3:*

    **Abordagem:** Integração com Chart.js via vue-chartjs.

    **Justificativa:** Optei por uma biblioteca robusta e amplamente utilizada no mercado. O uso de gráficos de barras para as "Top 5 Operadoras" permite uma análise comparativa imediata do volume financeiro, transformando dados brutos em informação visual clara, conforme as melhores práticas de Business Intelligence (BI).

    *Estratégia de Busca e Filtro (Parte 4.3.1):*

    **Opção Escolhida:** Opção A (Busca no Servidor).

    **Justificativa:** Optei por realizar o processamento dos filtros diretamente no backend através de queries SQL. Esta abordagem é mais eficiente para o navegador do cliente, pois evita o download de toda a base de dados para a memória local, garantindo rapidez mesmo em dispositivos com hardware limitado.

    *Gerenciamento de Estado (Parte 4.3.2):*

    **Abordagem:** Opção C (Composables - Vue 3).

    **Justificativa:** Para a complexidade deste teste, utilizei o padrão de Composables (Composition API). Isso permitiu organizar a lógica de busca e paginação de forma modular e reutilizável, sem a sobrecarga de configurar bibliotecas de estado global como Pinia ou Vuex, mantendo o código moderno e limpo.

    *Performance da Tabela (Parte 4.3.3):*

    **Estratégia:** Paginação Orientada a Dados.

    **Justificativa:** Em vez de renderizar centenas de linhas simultaneamente, o que causaria gargalos de performance no DOM (Document Object Model), a interface renderiza apenas 10 registros por vez. Isso assegura uma navegação fluida e tempos de resposta instantâneos ao alternar entre as páginas.

    **Decisão Técnica:** Ao mudar de página no componente Vue, uma nova requisição é disparada para a API com os parâmetros page e limit atualizados. Isso garante que a interface permaneça rápida e responsiva, independentemente do crescimento da base de dados no PostgreSQL.

    *Tratamento de Erros e Estados (Parte 4.3.4):*

    **Abordagem:** Feedback Visual Específico.

    **Análise Crítica:** Implementei estados de Loading (indicadores de carregamento) e mensagens de erro descritivas (ex: "Falha na conexão com a API"). Decidi por mensagens específicas em vez de genéricas para facilitar o diagnóstico de problemas pelo usuário e garantir que a interface nunca pareça "travada" em caso de falhas de rede.

## Tratamento de Inconsistências

Para cumprir os requisitos da Parte 1.3, o projeto realiza:

    - Limpeza de CNPJ: Agrupamento e soma de registros duplicados por período.

    - Filtragem de Valores: Remoção de despesas zeradas ou negativas, consideradas inconsistências para a análise.

    - Padronização de Datas: Normalização automática de trimestres e anos para colunas específicas.

## Limitações
Algumas estruturas de pastas internas nos ZIPs muito divergentes podem exigir ajustes no Regex de busca.
