"""
ans_client.py

Responsável por acessar o repositório de Dados Abertos da ANS,
identificar dinamicamente os últimos trimestres disponíveis de
Demonstrações Contábeis e realizar o download dos arquivos ZIP.

Decisões técnicas:
- Utiliza scraping simples de HTML (requests + BeautifulSoup),
  pois não há API estruturada para listagem de diretórios.
- Não assume estrutura fixa de anos ou trimestres.
- Implementação pronta para lidar com enventuais variações na estrutura.
"""

import os
import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

BASE_URL = "https://dadosabertos.ans.gov.br/FTP/PDA/demonstracoes_contabeis/"
RAW_DATA_DIR = "data/raw"



def get_available_years():
    """
    Retorna uma lista de anos disponíveis no repositório da ANS,
    ordenada do mais recente para o mais antigo.
    """
    response = requests.get(BASE_URL)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    year_links = []

    for link in soup.find_all("a"):
        href = link.get("href", "")
        if re.match(r"^\d{4}/$", href):
            year_links.append(href.strip("/"))

    return sorted(year_links, reverse=True)


def get_quarter_files(year):
    """
    Dado um ano, retorna os arquivos ZIP de trimestres disponíveis
    naquele ano, ordenados do mais recente para o mais antigo.
    """
    year_url = urljoin(BASE_URL, f"{year}/")
    response = requests.get(year_url)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    quarter_files = []

    for link in soup.find_all("a"):
        href = link.get("href", "")
        if re.match(r"^\dT\d{4}\.zip$", href):
            quarter_files.append(href)

    # Ordena considerando o número do trimestre
    quarter_files.sort(reverse=True)
    return quarter_files


def get_last_three_quarters():
    """
    Identifica os últimos três trimestres disponíveis,
    mesmo que estejam distribuídos entre anos diferentes.
    """
    last_quarters = []

    for year in get_available_years():
        quarters = get_quarter_files(year)
        for quarter in quarters:
            last_quarters.append((year, quarter))
            if len(last_quarters) == 3:
                return last_quarters

    return last_quarters


def download_quarters(quarters):
    """
    Realiza o download dos arquivos ZIP dos trimestres informados.
    """
    os.makedirs(RAW_DATA_DIR, exist_ok=True)

    for year, filename in quarters:
        file_url = urljoin(BASE_URL, f"{year}/{filename}")
        local_path = os.path.join(RAW_DATA_DIR, filename)

        if os.path.exists(local_path):
            continue  # evita download duplicado

        response = requests.get(file_url)
        response.raise_for_status()

        with open(local_path, "wb") as f:
            f.write(response.content)


if __name__ == "__main__":
    quarters = get_last_three_quarters()
    download_quarters(quarters)
