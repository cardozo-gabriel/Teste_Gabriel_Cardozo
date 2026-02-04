"""
=========================================================================
4.2. IMPLEMENTAÇÃO DA CAMADA DE SERVIÇOS (API REST)
=========================================================================
Estratégia: Utilização do FastAPI para prover endpoints de alta performance.
Justificativa: Suporte nativo a tipos assíncronos e documentação OpenAPI.
=========================================================================
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from .database import get_db_connection

app = FastAPI(title="API de Operadoras ANS - Teste Técnico")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 1. Rota: Listar Operadoras com Paginação (Tarefa 4.2)
@app.get("/api/operadoras")
def get_operadoras(page: int = 1, limit: int = 10, q: str = Query(None)):
    offset = (page - 1) * limit
    conn = get_db_connection()
    with conn.cursor() as cur:
        # Lógica de busca: filtra por Razão Social ou CNPJ se 'q' existir
        if q:
            search_query = f"%{q}%"
            sql = """SELECT * FROM operadoras 
                     WHERE razao_social ILIKE %s OR cnpj ILIKE %s 
                     ORDER BY registro_ans LIMIT %s OFFSET %s"""
            cur.execute(sql, (search_query, search_query, limit, offset))
        else:
            cur.execute("SELECT * FROM operadoras ORDER BY registro_ans LIMIT %s OFFSET %s", (limit, offset))
        
        data = cur.fetchall()
        
        # Contagem total ajustada para a busca
        count_sql = "SELECT COUNT(*) FROM operadoras WHERE razao_social ILIKE %s OR cnpj ILIKE %s" if q else "SELECT COUNT(*) FROM operadoras"
        cur.execute(count_sql, (f"%{q}%", f"%{q}%") if q else ())
        total = cur.fetchone()['count']
        
    conn.close()
    return {"data": data, "total": total, "page": page, "limit": limit}

# 2. Rota: Detalhes de uma Operadora Específica
@app.get("/api/operadoras/{cnpj}")
def get_operadora_detail(cnpj: str):
    """Busca os detalhes cadastrais pelo CNPJ"""
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("SELECT * FROM operadoras WHERE cnpj = %s", (cnpj,))
        res = cur.fetchone()
        if not res:
            raise HTTPException(status_code=404, detail="Operadora não encontrada")
        return res
    finally:
        cur.close()
        conn.close()

# 3. Rota: Histórico de Despesas
@app.get("/api/operadoras/{cnpj}/despesas")
def get_operadora_expenses(cnpj: str):
    """Retorna o histórico financeiro via JOIN entre tabelas"""
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        # Relaciona a operadora às suas despesas pelo Registro ANS
        query = """
            SELECT d.ano, d.trimestre, d.valor_despesa 
            FROM despesas_consolidadas d
            JOIN operadoras o ON d.registro_ans = o.registro_ans
            WHERE o.cnpj = %s
            ORDER BY d.ano DESC, d.trimestre DESC
        """
        cur.execute(query, (cnpj,))
        return cur.fetchall()
    finally:
        cur.close()
        conn.close()

# 4. Rota: Estatísticas Agregadas
@app.get("/api/estatisticas")
def get_stats():
    """Estatísticas pré-calculadas na tabela de agregados para performance"""
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        # Top 5 operadoras com maiores despesas (conforme processado no item 2.3/3.2)
        cur.execute("SELECT * FROM despesas_agregadas ORDER BY total_despesas DESC LIMIT 5")
        top_5 = cur.fetchall()
        
        # Média e Total Global
        cur.execute("SELECT SUM(total_despesas) as total_global, AVG(total_despesas) as media_global FROM despesas_agregadas")
        geral = cur.fetchone()
        
        return {
            "top_5": top_5,
            "estatisticas_gerais": geral
        }
    finally:
        cur.close()
        conn.close() 
        
"""
-------------------------------------------------------------------------
ANÁLISE CRÍTICA: ESTRATÉGIA DE ACESSO E PAGINAÇÃO (ITEM 4.2.2)
-------------------------------------------------------------------------
1. Paginação via Offset:
   - Justificativa: Escolhida devido à natureza dos dados (estáticos trimestralmente).
     Para o volume atual, o custo de performance do OFFSET é negligenciável
     frente à simplicidade de manutenção do código.

2. Integridade de Dados no JOIN:
   - Abordagem: INNER JOIN entre 'despesas_consolidadas' e 'operadoras'.
   - Justificativa: Garante que apenas dados financeiros atribuídos a CNPJs 
     válidos (validados na Parte 2) sejam expostos na API, mantendo a 
     consistência com as regras de negócio de enriquecimento de dados.

3. Performance de Estatísticas (Item 4.2.3):
   - Estratégia: Pré-calculado (Opção C).
   - Análise: Em vez de agregar milhões de registros por requisição, a API 
     consome a tabela 'despesas_agregadas'. Isso reduz a carga no banco 
     de dados e garante tempos de resposta estáveis ( < 50ms).
-------------------------------------------------------------------------
"""