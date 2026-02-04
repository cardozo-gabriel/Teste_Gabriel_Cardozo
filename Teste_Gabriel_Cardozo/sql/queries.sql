/* =========================================================================
   3.4. DESENVOLVIMENTO DE QUERIES ANALÍTICAS
   =========================================================================
*/

-- QUERY 1: Top 5 operadoras com maior crescimento percentual de despesas.
-- Comparação entre o 1º trimestre (início) e o 3º trimestre (fim) de 2025.
WITH valores_trimestres AS (
    SELECT 
        registro_ans,
        MAX(CASE WHEN trimestre = 1 THEN valor_despesa END) as v_inicial,
        MAX(CASE WHEN trimestre = 3 THEN valor_despesa END) as v_final
    FROM despesas_consolidadas
    GROUP BY registro_ans
)
SELECT 
    o.razao_social,
    vt.v_inicial,
    vt.v_final,
    ROUND(((vt.v_final - vt.v_inicial) / NULLIF(vt.v_inicial, 0)) * 100, 2) as crescimento_percentual
FROM valores_trimestres vt
JOIN operadoras o ON vt.registro_ans = o.registro_ans
WHERE vt.v_inicial IS NOT NULL AND vt.v_final IS NOT NULL
ORDER BY crescimento_percentual DESC
LIMIT 5;

/* JUSTIFICATIVA Q1 - TRATAMENTO DE DADOS FALTANTES: 
   Decidi ignorar operadoras que não possuem dados em ambos os trimestres comparativos. 
   Justificativa: Um cálculo de crescimento percentual sem uma base inicial (v_inicial) 
   ou final (v_final) resultaria em valores nulos ou infinitos, distorcendo o ranking 
   de performance real entre as operadoras ativas em todo o período.
*/


-- QUERY 2: Distribuição de despesas por UF e média por operadora.
-- Lista os 5 estados com maiores despesas totais.
SELECT 
    uf, 
    SUM(total_despesas) as despesa_total_uf,
    ROUND(AVG(total_despesas), 2) as media_despesa_por_operadora
FROM despesas_agregadas
GROUP BY uf
ORDER BY despesa_total_uf DESC
LIMIT 5;


-- QUERY 3: Operadoras com despesas acima da média geral em pelo menos 2 trimestres.
WITH media_geral AS (
    SELECT AVG(valor_despesa) as valor_medio FROM despesas_consolidadas
),
contagem_acima AS (
    SELECT 
        registro_ans, 
        COUNT(*) as trimestres_acima
    FROM despesas_consolidadas, media_geral
    WHERE valor_despesa > valor_medio
    GROUP BY registro_ans
)
SELECT o.razao_social, c.trimestres_acima
FROM contagem_acima c
JOIN operadoras o ON c.registro_ans = o.registro_ans
WHERE c.trimestres_acima >= 2;

/* TRADE-OFF TÉCNICO Q3 - PERFORMANCE VS LEGIBILIDADE:
   Escolhi a abordagem de CTE (Common Table Expression) com Join Lateral. 
   Justificativa: Esta abordagem é mais legível e facilita a manutenção do código. 
   Em termos de performance, o banco de dados calcula a média global apenas uma vez 
   antes de realizar a comparação, sendo superior a uma subquery correlacionada 
   que seria executada para cada linha da tabela.
*/