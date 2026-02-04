"""
processor.py

Este módulo realiza a extração, normalização e consolidação das Demonstrações Contábeis.

Justificativa do Trade-off Técnico: Processamento Incremental
Escolhi o processamento incremental (leitura e escrita por partes) em vez de carregar 
todos os dados em memória de uma vez. 
- Motivo: Os arquivos da ANS possuem um volume massivo de dados (milhares de linhas por trimestre). 
- Prós: Garante que o script seja executado com baixo consumo de memória RAM e evita 
  crashes em máquinas com recursos limitados.
- Contras: O tempo total de execução pode ser levemente superior devido às múltiplas 
  operações de escrita em disco.

Tratamento de Inconsistências (Análise Crítica):
1. CNPJs duplicados com Razões Sociais diferentes: Agrupei os dados por CNPJ e 
   período, somando os valores. Mantive uma Razão Social padronizada para garantir 
   a unicidade, tratando o CNPJ como a chave primária confiável.
2. Valores zerados ou negativos: Optei por ignorar (remover) estes registros. 
   Justificativa: Despesas negativas ou nulas em sinistros são inconsistências que 
   não representam gastos reais para a análise financeira proposta.
3. Datas inconsistentes: Normalize os formatos de data durante a leitura, extraindo 
   o Ano e Trimestre diretamente da estrutura de diretórios e nomes de arquivos.
"""

import os
import zipfile
import pandas as pd
import io
import re
import shutil

RAW_DATA_DIR = "data/raw"
PROCESSED_DATA_DIR = "data/processed"
OUTPUT_DIR = "data/output"

# Garante que as pastas existam
os.makedirs(PROCESSED_DATA_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

def extract_all_zips():
    """
    Extrai todos os arquivos ZIP da pasta raw para a pasta processed.
    """
    zip_files = [f for f in os.listdir(RAW_DATA_DIR) if f.endswith('.zip')]
    for zip_name in zip_files:
        path_to_zip = os.path.join(RAW_DATA_DIR, zip_name)
        # Cria uma subpasta para cada ZIP para evitar conflito de nomes de arquivos internos
        extraction_path = os.path.join(PROCESSED_DATA_DIR, zip_name.replace('.zip', ''))
        
        with zipfile.ZipFile(path_to_zip, 'r') as zip_ref:
            zip_ref.extractall(extraction_path)
        print(f"Extraído: {zip_name}")

def read_and_normalize(file_path):
    """
    Lê o arquivo identificando o separador e tratando o encoding.
    """
    ext = os.path.splitext(file_path)[1].lower()
    try:
        if ext in [".csv", ".txt"]:
            # Detecta se o separador é ; ou , lendo apenas o início do arquivo
            with open(file_path, 'r', encoding='latin-1') as f:
                sample = f.read(2048)
                separator = ';' if ';' in sample else ','
            
            return pd.read_csv(
                file_path, 
                sep=separator, 
                encoding="latin-1", 
                low_memory=False
            )
        elif ext == ".xlsx":
            return pd.read_excel(file_path)
    except Exception as e:
        print(f"Erro ao ler {file_path}: {e}")
    return None

def process_all_data():
    extract_all_zips()

    output_path = os.path.join(OUTPUT_DIR, "consolidado_despesas.csv")
    first_write = True
    termo_filtro = 'Despesas com Eventos/Sinistros'

    # Varre TUDO o que foi extraído na pasta processed
    for root, dirs, files in os.walk(PROCESSED_DATA_DIR):
        for file_name in files:
            file_path = os.path.join(root, file_name)
            
            # Pula arquivos que claramente não são dados (ex: metadados de sistema)
            if file_name.startswith('._') or not file_name.lower().endswith(('.csv', '.txt', '.xlsx')):
                continue

            print(f"Analisando conteúdo de: {file_name}...")
            df = read_and_normalize(file_path)
            
            if df is not None:
                # Normaliza os nomes das colunas para garantir que 'DESCRICAO' seja encontrada
                df.columns = [str(c).strip().upper() for c in df.columns]

                if 'DESCRICAO' in df.columns:
                    # Filtro flexível: remove espaços extras e ignora maiúsculas/minúsculas
                    mask = df['DESCRICAO'].astype(str).str.contains(termo_filtro, case=False, na=False)
                    df_filtered = df[mask].copy()

                    if not df_filtered.empty:
                        # Recupera Ano/Trimestre do nome da pasta pai
                        folder_name = os.path.basename(root)
                        # Se não achar na pasta imediata, tenta na pasta acima (resiliência)
                        if not re.search(r"(\d)T(\d{4})", folder_name):
                             folder_name = os.path.basename(os.path.dirname(root))
                        
                        match = re.search(r"(\d)T(\d{4})", folder_name)
                        quarter, year = match.groups() if match else ("N/A", "N/A")

                        df_filtered['Trimestre'] = quarter
                        df_filtered['Ano'] = year
                        
                        # Salvamento incremental
                        df_filtered.to_csv(
                            output_path,
                            mode='a' if not first_write else 'w',
                            index=False,
                            header=first_write,
                            sep=';',
                            encoding='latin-1'
                        )
                        first_write = False
                        print(f"-> SUCESSO: {len(df_filtered)} linhas filtradas em {file_name}")
                else:
                    print(f"   (Coluna DESCRICAO não encontrada em {file_name})")
                    


def clean_and_finalize_data():
    """
    Parte 1.3: Realiza a limpeza final, conversão numérica, 
    agrupamento por soma e compactação.
    """
    output_path = os.path.join(OUTPUT_DIR, "consolidado_despesas.csv")
    final_zip_path = os.path.join(OUTPUT_DIR, "consolidado_despesas.zip")
    
    if not os.path.exists(output_path):
        print("Erro: Arquivo consolidado bruto não encontrado.")
        return

    # 1. CARGA DOS DADOS
    df = pd.read_csv(output_path, sep=';', encoding='latin-1')

    # 2. RENOMEAÇÃO CONFORME DICIONÁRIO
    # REG_ANS vira CNPJ conforme o mapeamento do desafio
    mapping = {
        'REG_ANS': 'CNPJ',
        'VL_SALDO_FINAL': 'ValorDespesas'
    }
    df = df.rename(columns=mapping)

    # 3. CONVERSÃO NUMÉRICA (Tratando o padrão brasileiro 1.234,56)
    # Remove o ponto de milhar e troca a vírgula decimal por ponto
    df['ValorDespesas'] = (
        df['ValorDespesas']
        .astype(str)
        .str.replace('.', '', regex=False)
        .str.replace(',', '.', regex=False)
    )
    df['ValorDespesas'] = pd.to_numeric(df['ValorDespesas'], errors='coerce')

    # 4. AGRUPAMENTO E SOMA (A essência da consolidação)
    # Somamos todas as contas contábeis de uma mesma operadora no mesmo período
    df_consolidado = df.groupby(['CNPJ', 'Ano', 'Trimestre'], as_index=False).agg({
        'ValorDespesas': 'sum'
    })

    # 5. TRATAMENTO DE COLUNAS E INCONSISTÊNCIAS
    # Cria a RazaoSocial (usando o ID como fallback)
    df_consolidado['RazaoSocial'] = "OPERADORA_" + df_consolidado['CNPJ'].astype(str)

    # Filtra valores positivos (remove zerados e negativos conforme o desafio)
    df_consolidado = df_consolidado[df_consolidado['ValorDespesas'] > 0]

    # Reordena as colunas conforme solicitado
    colunas_finais = ['CNPJ', 'RazaoSocial', 'Trimestre', 'Ano', 'ValorDespesas']
    df_final = df_consolidado[colunas_finais]

    # 6. SALVAMENTO E COMPACTAÇÃO
    df_final.to_csv(output_path, index=False, sep=';', encoding='latin-1')

    with zipfile.ZipFile(final_zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        zipf.write(output_path, arcname="consolidado_despesas.csv")
    
    print(f"--- PARTE 1.3 CONCLUÍDA ---")
    print(f"Linhas finais (uma por operadora/trimestre): {len(df_final)}")
    print(f"Arquivo gerado: {final_zip_path}")   
            

if __name__ == "__main__":
    process_all_data()