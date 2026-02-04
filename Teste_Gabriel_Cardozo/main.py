import sys
import os

# Ajusta o path para encontrar o conteúdo em 'src'
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))

from src.ans_client import get_last_three_quarters, download_quarters
from src.processor import process_all_data, clean_and_finalize_data
# Importamos as duas funções do enricher
from src.enricher import execute_transformation_pipeline, export_to_sql_ready_files

def main():
    print("=== INICIANDO PIPELINE DE DADOS ANS ===")
    
    try:
        # Passos 1 a 3 (Seus passos já existentes)
        print("\n[1/5] Buscando arquivos no site da ANS...")
        quarters = get_last_three_quarters()
        if not quarters:
            print("Nenhum arquivo encontrado.")
            return
        download_quarters(quarters)
        
        print("\n[2/5] Extraindo e filtrando despesas...")
        process_all_data()
        
        print("\n[3/5] Executando análise crítica e gerando ZIP final...")
        clean_and_finalize_data()
        
        # Passo 4: Enriquecimento e Validação
        print("\n[4/5] Iniciando Validação e Enriquecimento (Parte 2.1 e 2.2)...")
        # Capturamos os DataFrames resultantes aqui
        df_enriquecido, df_agregado = execute_transformation_pipeline()

        # Passo 5: Exportação para o Banco de Dados (Parte 3.3)
        # Passamos os DataFrames capturados para a função de limpeza SQL
        export_to_sql_ready_files(df_enriquecido, df_agregado)

        print("\n=== PROCESSO FINALIZADO COM SUCESSO! ===")
        print("Agora você pode executar o script 'sql/import.sql' no seu banco de dados.")

    except Exception as e:
        print(f"\n[ERRO]: Falha na execução: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()