/* =========================================================================
   3.2. DEFINIÇÃO DE ESTRUTURA (DDL) E JUSTIFICATIVAS TÉCNICAS
   =========================================================================
   
   **Optei por utilizar SQL compatível com PostgreSQL > 10.0**

   1. ESCOLHA DE NORMALIZAÇÃO: OPÇÃO B (TABELAS NORMALIZADAS SEPARADAS)
   -------------------------------------------------------------------------
   Justificativa baseada nos critérios do teste:
   - Volume de Dados: A separação evita a redundância de dados cadastrais (Razão Social, CNPJ) 
     repetidos para cada registro financeiro, otimizando o armazenamento em disco.
   - Frequência de Atualização: Alterações em dados cadastrais (como mudança de nome ou UF) 
     exigem o update em apenas uma linha na tabela 'operadoras', mantendo a integridade.
   - Complexidade Analítica: Facilita o uso de Joins estruturados e permite que índices 
     específicos por CNPJ ou UF sejam mais eficientes do que em uma tabela gigante.

   2. ESCOLHA DOS TIPOS DE DADOS
   -------------------------------------------------------------------------
   - Valores Monetários (DECIMAL vs FLOAT vs INTEGER):
     Escolha: DECIMAL(18, 2). O uso de FLOAT é inadequado para finanças devido a erros 
     de arredondamento de precisão binária. O INTEGER (em centavos) é performático, mas 
     o DECIMAL garante legibilidade direta e a precisão contábil exigida.
   
   - Datas/Períodos (DATE vs VARCHAR vs TIMESTAMP):
     Escolha: INTEGER para 'ano' e 'trimestre'. Como os dados da ANS são puramente 
     trimestrais, armazenar como INTEGER é mais leve que TIMESTAMP e simplifica 
     filtros e ordenações analíticas sem a sobrecarga de fusos horários.
   =========================================================================
*/

-- 1. Tabela de Cadastro das Operadoras
CREATE TABLE operadoras (
    registro_ans VARCHAR(20) PRIMARY KEY, 
    cnpj VARCHAR(14) NOT NULL UNIQUE,     --
    razao_social VARCHAR(255) NOT NULL,
    modalidade VARCHAR(100),
    uf CHAR(2)
);

-- 2. Tabela de Despesas Consolidadas (Baseada no item 1.3)
CREATE TABLE despesas_consolidadas (
    id SERIAL PRIMARY KEY,                -- Chave Primária autoincremento
    registro_ans VARCHAR(20) NOT NULL,
    ano INT NOT NULL,
    trimestre INT NOT NULL,
    valor_despesa DECIMAL(18, 2) NOT NULL, 
    
    
    CONSTRAINT fk_operadora FOREIGN KEY (registro_ans) REFERENCES operadoras(registro_ans)
);

-- 3. Tabela para Dados Agregados (Baseada no item 2.3)
CREATE TABLE despesas_agregadas (
    razao_social VARCHAR(255),
    uf CHAR(2),
    total_despesas DECIMAL(18, 2),
    media_trimestral DECIMAL(18, 2),
    desvio_padrao DECIMAL(18, 2),
    PRIMARY KEY (razao_social, uf) -- Chave Composta
);

-- Índices para otimizar buscas frequentes
CREATE INDEX idx_despesas_periodo ON despesas_consolidadas(ano, trimestre);
CREATE INDEX idx_operadoras_cnpj ON operadoras(cnpj);