# main.py
import requests
import pytz
import schedule
import time
import os
from dotenv import load_dotenv
from datetime import datetime
from bs4 import BeautifulSoup
from db import collection  # Importando a conexão com o banco de dados MongoDB
from db import collection_main


def scrape_and_save_data(number, country, link_number):
    load_dotenv()
    # URL do site para fazer o scraping
    url = f"https://www.receivesms.co{link_number}"

    # Fazendo a requisição HTTP
    response = requests.get(url)

    # Verificando se a requisição foi bem-sucedida
    if response.status_code == 200:
        # Obtendo o conteúdo da página
        page_content = response.text

        # Parseando o conteúdo com BeautifulSoup
        soup = BeautifulSoup(page_content, "html.parser")

        # Encontrando todas as divs com a classe "row border-bottom table-hover" dentro da div principal
        message_divs = soup.select("div#msgtbl > div.row.border-bottom.table-hover")

        # Loop para percorrer cada div com a classe especificada
        for div in message_divs:
            # Verificando se a linha contém "ADS" em qualquer formato, se sim, não processamos a linha
            if "ADS" in div.get_text(strip=True).lower():
                continue

            # Obtendo o conteúdo da div com a classe "col-xs-12 col-md-2" que contém o "from_de"
            from_de = div.select_one("div.col-xs-12.col-md-2").get_text(strip=True)

            # Obtendo o conteúdo da div com a classe "col-xs-12 col-md-8" que contém o "content_message"
            content_message = div.select_one("div.col-xs-12.col-md-8").get_text(strip=True)

            # Removendo o "h" do início do conteúdo da mensagem, se estiver presente
            if content_message.startswith("h "):
                content_message = content_message[2:]

            # Encontrando o segundo "h" no conteúdo da mensagem
            second_h_index = content_message.find("h", 1)

            paulownia_tz = pytz.timezone('America/Sao_Paulo')
            brasil_datetime = datetime.now(paulownia_tz)
            timestamp_unix = int(brasil_datetime.timestamp())

            # Exemplo de como cadastrar os resultados no banco de dados MongoDB
            existing_message = collection.find_one({"content_message": content_message[second_h_index + 1:].strip()})

            if not existing_message:
                data = {
                    "number_sim": number,
                    "from_de": from_de,
                    "content_message": content_message[second_h_index + 1:].strip(),
                    "country": country,
                    "data_created": timestamp_unix,
                    "site": "receivesms_co",
                    "active": True
                }
                collection.insert_one(data)


def scrape_recent_data():
    try:
        numbers = collection_main.find(
            {"site": "receivesms_co", "active": True, "link_country": os.getenv("LINK_COUNTRY")}).sort("data_created",
                                                                                                       -1).limit(12)
        processed_numbers = set()
        for number in numbers:
            link_country = os.getenv("LINK_COUNTRY")
            number_page = number["number_page"]
            link_number = "/" + link_country + "/" + number_page + "/"

            if number["number_sim"] not in processed_numbers:
                scrape_and_save_data(number["number_sim"], number["country"], link_number)
                processed_numbers.add(number["number_sim"])

        # print(f"Números Processados: {len(processed_numbers)}")
    except Exception as error:
        print("Erro:", error)


def job():
    # print("Iniciando scraping...")
    scrape_recent_data()
    # print("Scraping concluído.")


# Agendando a execução do job a cada 5 segundos
schedule.every(5).seconds.do(job)

while True:
    schedule.run_pending()
    time.sleep(1)
