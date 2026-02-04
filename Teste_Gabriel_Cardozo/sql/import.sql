/* =========================================================================
   3.3. IMPORTAÇÃO E ANÁLISE CRÍTICA DE DADOS (DML)
   =========================================================================
   Estratégia: Utilização do comando COPY (PostgreSQL) para carga de alto volume.
   Nota: Os caminhos abaixo devem ser ajustados para o diretório local do projeto.
   =========================================================================
*/

-- 1. IMPORTAÇÃO: Cadastro de Operadoras
-- O arquivo 'sql_operadoras.csv' foi pré-processado em Python para conter apenas as 5 colunas do schema.
COPY operadoras(registro_ans, cnpj, razao_social, modalidade, uf)
FROM 'C:/CAMINHO_PARA_O_PROJETO/data/output/sql_operadoras.csv' 
WITH (FORMAT csv, HEADER true, DELIMITER ';', ENCODING 'UTF8');

-- 2. IMPORTAÇÃO: Despesas Consolidadas
COPY despesas_consolidadas(registro_ans, ano, trimestre, valor_despesa)
FROM 'C:/CAMINHO_PARA_O_PROJETO/data/output/sql_despesas.csv' 
WITH (FORMAT csv, HEADER true, DELIMITER ';', ENCODING 'UTF8');

-- 3. IMPORTAÇÃO: Dados Agregados
COPY despesas_agregadas(razao_social, uf, total_despesas, media_trimestral, desvio_padrao)
FROM 'C:/CAMINHO_PARA_O_PROJETO/data/output/sql_agregadas.csv' 
WITH (FORMAT csv, HEADER true, DELIMITER ';', ENCODING 'UTF8');

/* -------------------------------------------------------------------------
   ANÁLISE CRÍTICA: TRATAMENTO DE INCONSISTÊNCIAS (ITEM 3.3)
   -------------------------------------------------------------------------
   Durante o processo de ETL, as seguintes situações foram tratadas:

   1. Valores NULL em campos obrigatórios:
      - Abordagem: REJEITAR.
      - Justificativa: Campos como 'registro_ans' e 'valor_despesa' são chaves primárias ou 
        bases de cálculo. No schema (3.2), definimos NOT NULL. Registros nulos são 
        descartados via script Python antes da carga para garantir a integridade estatística.

   2. Strings em campos numéricos:
      - Abordagem: TENTAR CONVERSÃO / LIMPEZA.
      - Justificativa: Valores monetários no CSV original utilizam padrão brasileiro (vírgula). 
        O pipeline Python limpa caracteres não numéricos e converte para float (ponto decimal).
        O tipo DECIMAL no SQL atua como validador final; se houver string, a carga é interrompida.

   3. Datas em formatos inconsistentes:
      - Abordagem: USAR VALOR PADRÃO / CONVERSÃO.
      - Justificativa: A granularidade dos dados da ANS é trimestral. Em vez de lidar com
        inconsistências de formatos de data (DD/MM vs MM/DD), os dados foram convertidos 
        em colunas de INTEIROS (Ano e Trimestre). Isso elimina ambiguidade e otimiza a performance.
   -------------------------------------------------------------------------
*/