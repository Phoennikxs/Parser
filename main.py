# main.py

import sys
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

from parser.avito_parser import parse_avito
from parser.drom_parser import parse_drom

# Добавляем полный путь к каталогу db
sys.path.append('/home/kali/scraper/Parser-main/db')

# Импортируем функцию для вставки данных
from db.database import insert_into_db

def setup_driver():
    """Функция для настройки драйвера Selenium"""
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # без GUI
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    # Указываем путь к драйверу Chrome
    service = Service("/usr/local/bin/chromedriver")
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver

def main():
    # Настроим драйвер
    driver = setup_driver()

    try:
        # URL для парсинга с Avito
        avito_base_url = "https://www.avito.ru/taganrog/zapchasti_i_aksessuary/zapchasti_i_aksessuary/zapchasti_dlya_to-ASgBAgICAUSsvhPw_I0D?cd=1"
        max_pages = 2  # Сколько страниц парсим
        avito_collected = parse_avito()

        # URL для парсинга с Drom
        drom_url = "https://baza.drom.ru/taganrog/sell_spare_parts/+/%E7%E0%EF%F7%E0%F1%F2%E8+%E4%EB%FF+%D2%CE/"
        target_count = 50  # Сколько объявлений собираем
        drom_collected = parse_drom()

        print(f"Парсинг завершён. Собрано объявлений на Drom: {len(drom_collected)}. На Avito: {len(avito_collected)}.")
    finally:
        driver.quit()

if __name__ == "__main__":
    main()
