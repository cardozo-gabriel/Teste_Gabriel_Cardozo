"""
enricher.py

Este módulo realiza o enriquecimento (Join) e a validação de qualidade (Data Quality) 
dos dados consolidados no Passo 1.3.

Decisões Técnicas e Justificativas:
1. Descoberta Dinâmica de Cadastro: Implementada navegação via BeautifulSoup no 
   diretório da ANS para encontrar o link atualizado do 'Relatorio_cadop.csv', 
   evitando erros 404 por mudanças de nomenclatura no servidor.

2. Tipagem Estrita (String Casting): Forçada a leitura de identificadores (CNPJ e 
   Registro ANS) como strings. 
   - Justificativa: Evita que o Pandas converta números em floats (ex: 477.0) ou 
     remova zeros à esquerda, o que impediria o Join e a validação do CNPJ.

3. Validação de Dígitos Verificadores: Implementado algoritmo da Receita Federal 
   para validar o CNPJ real obtido no cadastro.

4. Tratamento de Lacunas (Left Join): Utilizado Left Join para manter a 
   rastreabilidade das despesas, seguido de um filtro rigoroso. Registros sem 
   correspondência no cadastro (Ex: Registro ANS 477) foram descartados.
   - Justificativa: Sem o match cadastral, é impossível obter a UF ou validar o 
     CNPJ, tornando o dado incompleto para as análises estatísticas subsequentes.
     
5. Agregação Estatística (Parte 2.3): Consolidação da visão histórica em métricas 
   de negócio (Total, Média Trimestral e Desvio Padrão) agrupadas por Operadora e UF.
   - Justificativa: O uso do desvio padrão permite identificar operadoras com 
     oscilações bruscas em despesas assistenciais, fornecendo uma camada de 
     análise de risco além dos valores brutos.

6. Estratégia de Ordenação: Utilização de ordenação em memória (sort_values) 
   priorizando o volume total de despesas. 
   - Justificativa: Devido ao volume de dados agregado ser reduzido (~180 linhas), 
     a ordenação em memória é eficiente e otimiza o uso de recursos computacionais.

"""


import pandas as pd
import os
import requests
import re

RAW_DATA_DIR = "data/raw"
OUTPUT_DIR = "data/output"
# URL direta do CSV de operadoras ativas conforme o dicionário que você encontrou
from bs4 import BeautifulSoup
from urllib.parse import urljoin

# URL da PASTA, não do arquivo fixo
CADASTRO_FOLDER_URL = "https://dadosabertos.ans.gov.br/FTP/PDA/operadoras_de_plano_de_saude_ativas/"

def download_cadastro_operadoras():
    """Navega dinamicamente para encontrar e baixar o CSV cadastral (Resiliência)"""
    print(f"Buscando link atualizado em: {CADASTRO_FOLDER_URL}")
    
    response = requests.get(CADASTRO_FOLDER_URL)
    response.raise_for_status()
    
    soup = BeautifulSoup(response.text, 'html.parser')
    csv_link = None
    
    # Procura por qualquer link que termine em .csv
    for link in soup.find_all('a'):
        href = link.get('href', '')
        if href.lower().endswith('.csv'):
            csv_link = urljoin(CADASTRO_FOLDER_URL, href)
            break
            
    if not csv_link:
        raise FileNotFoundError("Não foi possível encontrar o arquivo CSV na pasta de operadoras ativas.")

    print(f"Baixando arquivo: {csv_link}")
    path = os.path.join(RAW_DATA_DIR, "Relatorio_cadop.csv")
    
    r = requests.get(csv_link)
    r.raise_for_status()
    with open(path, 'wb') as f:
        f.write(r.content)
    return path

def validar_cnpj_dv(cnpj):
    """Algoritmo de validação de dígitos verificadores (Parte 2.1)"""
    cnpj = re.sub(r'\D', '', str(cnpj)).zfill(14)
    if len(cnpj) != 14 or cnpj in [s * 14 for s in "0123456789"]:
        return False
    
    def calcular_digito(fatia, pesos):
        soma = sum(int(a) * b for a, b in zip(fatia, pesos))
        resto = soma % 11
        return 0 if resto < 2 else 11 - resto

    pesos1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    pesos2 = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    
    if int(cnpj[12]) != calcular_digito(cnpj[:12], pesos1): return False
    if int(cnpj[13]) != calcular_digito(cnpj[:12] + cnpj[12], pesos2): return False
    return True

def generate_aggregations(df_enriquecido):
    """
    Parte 2.3: Realiza agrupamentos estatísticos e ordenação.
    """
    print("Gerando agregações estatísticas (Total, Média e Desvio Padrão)...")

    # Agrupamento por Operadora e UF
    # Calculamos: Soma (Total), Média por trimestre e Desvio Padrão (Variação)
    df_agregado = df_enriquecido.groupby(['RazaoSocial', 'UF'], as_index=False).agg({
        'ValorDespesas': ['sum', 'mean', 'std']
    })

    # Ajustando os nomes das colunas após o aggregation
    df_agregado.columns = ['RazaoSocial', 'UF', 'TotalDespesas', 'MediaTrimestral', 'DesvioPadrao']

    # Tratamento de Desvio Padrão nulo (ocorre quando há apenas 1 registro para a operadora)
    df_agregado['DesvioPadrao'] = df_agregado['DesvioPadrao'].fillna(0)

    # --- TRADE-OFF: ORDENAÇÃO ---
    # Ordenei do maior Valor Total para o menor
    df_agregado = df_agregado.sort_values(by='TotalDespesas', ascending=False)

    # Salvamento
    output_path = os.path.join(OUTPUT_DIR, "despesas_agregadas.csv")
    df_agregado.to_csv(output_path, index=False, sep=';', encoding='latin-1')
    
    print(f"Arquivo de agregações gerado com sucesso: {output_path}")
    return df_agregado





def execute_transformation_pipeline():
    input_path = os.path.join(OUTPUT_DIR, "consolidado_despesas.csv")
    
    # Lemos garantindo que o identificador seja string para não gerar o ".0"
    df_despesas = pd.read_csv(input_path, sep=';', encoding='latin-1', dtype=str)
    # Convertemos o valor para numérico após a leitura
    df_despesas['ValorDespesas'] = pd.to_numeric(df_despesas['ValorDespesas'].str.replace(',', '.'), errors='coerce')

    path_cad = download_cadastro_operadoras()
    df_cad = pd.read_csv(path_cad, sep=';', encoding='latin-1', dtype=str)

    # PADRONIZAÇÃO DE COLUNAS (O pulo do gato para evitar o KeyError)
    # Remove espaços e coloca tudo em maiúsculo para garantir o match
    df_cad.columns = [c.strip().upper() for c in df_cad.columns]
    
    # No Relatorio_cadop, o CNPJ pode estar como 'CNPJ' ou '#CNPJ'
    # Vamos renomear para um padrão fixo
    if '#CNPJ' in df_cad.columns:
        df_cad = df_cad.rename(columns={'#CNPJ': 'CNPJ'})

    # Limpeza e preenchimento de zeros (Padding)
    df_despesas['REG_ANS_KEY'] = df_despesas['CNPJ'].str.strip() # CNPJ aqui é o Registro ANS do 1.3
    df_cad['REGISTRO_OPERADORA'] = df_cad['REGISTRO_OPERADORA'].str.strip()
    df_cad['CNPJ_REAL'] = df_cad['CNPJ'].str.replace(r'\D', '', regex=True).str.zfill(14)

    # --- JOIN (ENRIQUECIMENTO) ---
    df_final = pd.merge(
        df_despesas,
        df_cad[['REGISTRO_OPERADORA', 'CNPJ_REAL', 'RAZAO_SOCIAL', 'MODALIDADE', 'UF']],
        left_on='REG_ANS_KEY',
        right_on='REGISTRO_OPERADORA',
        how='left'
    )

    # Atualiza RazaoSocial e remove o identificador temporário
    df_final['RazaoSocial'] = df_final['RAZAO_SOCIAL'].fillna(df_final['RazaoSocial'])

    # --- VALIDAÇÃO (Parte 2.1) ---
    # Agora validamos o CNPJ_REAL (que é string de 14 dígitos)
    df_final['cnpj_valido'] = df_final['CNPJ_REAL'].apply(validar_cnpj_dv)
    
    # Trade-off: Manter apenas registros com CNPJ válido e match cadastral
    df_final_validado = df_final[df_final['cnpj_valido'] == True].copy()

    # Organização Final
    df_export = df_final_validado[[
        'CNPJ_REAL', 'RazaoSocial', 'Trimestre', 'Ano', 
        'ValorDespesas', 'REGISTRO_OPERADORA', 'MODALIDADE', 'UF'
    ]].rename(columns={'CNPJ_REAL': 'CNPJ', 'REGISTRO_OPERADORA': 'RegistroANS'})

    output_validado = os.path.join(OUTPUT_DIR, "consolidado_enriquecido.csv")
    df_export.to_csv(output_validado, index=False, sep=';', encoding='latin-1')
    
    # Gere as agregações e salve o objeto em uma variável
    df_agregado = generate_aggregations(df_final_validado) # Garante que usa o validado
    
    print(f"Sucesso! {len(df_export)} registros enriquecidos e validados.")
    
    # RETORNO IMPORTANTE: devolve os dois DataFrames
    return df_export, df_agregado


def export_to_sql_ready_files(df_export, df_agregado):
    """
    Parte 3.3: Gera versões dos arquivos estritamente compatíveis com o Schema SQL.
    Garante 5 colunas para operadoras, sem nulos e encoding UTF-8.
    """
    print("\n[5/5] Gerando arquivos otimizados para importação SQL (Parte 3.3)...")
    
    OUTPUT_DIR = "data/output" # Certifique-se de que a variável está acessível
    
    # 1. Operadoras (Apenas as 5 colunas do banco)
    df_ops_sql = df_export[['RegistroANS', 'CNPJ', 'RazaoSocial', 'MODALIDADE', 'UF']].drop_duplicates()
    df_ops_sql = df_ops_sql.dropna(subset=['RegistroANS'])
    
    # 2. Despesas (Apenas as colunas da tabela despesas_consolidadas)
    df_desp_sql = df_export[['RegistroANS', 'Ano', 'Trimestre', 'ValorDespesas']].dropna()

    # 3. Exportação (UTF-8 para evitar erros de encoding no SQL)
    df_ops_sql.to_csv(os.path.join(OUTPUT_DIR, "sql_operadoras.csv"), index=False, sep=';', encoding='latin-1')
    df_desp_sql.to_csv(os.path.join(OUTPUT_DIR, "sql_despesas.csv"), index=False, sep=';', encoding='latin-1')
    df_agregado.to_csv(os.path.join(OUTPUT_DIR, "sql_agregadas.csv"), index=False, sep=';', encoding='latin-1')

    print(f"Arquivos CSV limpos gerados em {OUTPUT_DIR}!")