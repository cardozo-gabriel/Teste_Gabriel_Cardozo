import psycopg2
from psycopg2.extras import RealDictCursor

def get_db_connection():
    """
    Estabelece a conexão com o banco de dados PostgreSQL.
    -------------------------------------------------------------------------
    NOTA PARA O AVALIADOR: 
    Ajuste as credenciais abaixo conforme a sua configuração local do PostgreSQL.
    -------------------------------------------------------------------------
    """
    return psycopg2.connect(
        host="localhost",
        database="ans_db",
        user="postgres",
        password="SUA_SENHA_AQUI", # <--- Substituir pela senha do seu banco
        port="5432",
        cursor_factory=RealDictCursor
    )