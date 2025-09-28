import sys
import os
import time
import json
import re
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

# Добавляем полный путь к каталогу db
sys.path.append('/home/kali/scraper/Parser-main/db')
# Теперь импортируем из db
from database import insert_into_db

# Настройки браузера
chrome_options = Options()
chrome_options.add_argument("--headless=new")  # Без графического интерфейса
chrome_options.add_argument("--disable-blink-features=AutomationControlled")  # Обход антибота
chrome_options.add_argument("--ignore-certificate-errors")  # Игнорировать ошибки SSL
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--disable-gpu")  # Отключает GPU-рендеринг
chrome_options.add_argument("--disable-webgl")  # Отключает WebGL (уже есть)
chrome_options.add_argument("--disable-webgpu")  # Полностью отключает WebGPU
chrome_options.add_argument("--use-angle=gl")  # Использует OpenGL вместо Direct3D
chrome_options.add_argument("--disable-software-rasterizer")  # Отключает программный рендеринг
chrome_options.add_argument("--disable-accelerated-2d-canvas")  # Отключает 2D-ускорение
chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36")

# Указываем путь к драйверу Chrome
service = Service("/usr/local/bin/chromedriver")
driver = webdriver.Chrome(service=service, options=chrome_options)

BASE_URL = "https://www.avito.ru/taganrog/zapchasti_i_aksessuary/zapchasti_i_aksessuary/zapchasti_dlya_to-ASgBAgICAUSsvhPw_I0D?cd=1&context=H4sIAAAAAAAA_wEmANn_YToxOntzOjE6InkiO3M6MTY6IjZ6OGxkM2s1MExnemdzMXgiO31ZlZ56JgAAAA"
MAX_PAGES = 100  # Ограничение на количество страниц


def parse_avito():
    """Парсинг Avito"""
    for page in range(2, MAX_PAGES + 1):
        url = f"{BASE_URL}&p={page}"  # Формируем ссылку для текущей страницы
        driver.get(url)
        time.sleep(5)

        try:
            # Ждем появления хотя бы одного объявления
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//*[contains(@class, 'iva-item-root')]"))
            )
        except TimeoutException:
            print(f"Страница {page} не загрузилась, пропускаем...")
            continue

        # Получаем список объявлений на текущей странице
        items = driver.find_elements(By.XPATH, "//*[contains(@class, 'iva-item-root')]")
        if not items:
            print(f"На странице {page} объявлений не найдено, заканчиваем парсинг.")
            break

        # Обработка каждого объявления
        for i, item in enumerate(items, start=1):
            try:
                title_element = WebDriverWait(item, 3).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, '[data-marker="item-title"]'))
                )
                title = title_element.text
                href = title_element.get_attribute("href")
                print(title)
                print(href)
            except TimeoutException:
                title = None
                href = None

            try:
                price_element = WebDriverWait(item, 3).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, '[data-marker="item-price"]'))
                )
                raw_price = price_element.text
                price_digits = re.sub(r'\D', '', raw_price)  # Извлекаем цифры
                price = int(price_digits) if price_digits else 0
                print(price)
            except TimeoutException:
                price = 0

            try:
                views_element = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, '[data-marker="item-view/total-views"]'))
                )
                raw_views = views_element.text  # например: "52 просмотра"
                # Оставляем только цифры
                views_digits = re.sub(r'\D', '', raw_views)
                views = int(views_digits) if views_digits else 0
                print(views)
            except TimeoutException:
                views = 0

            # Вставляем в базу данных
            insert_into_db(title, price, views, href)



    # Закрываем браузер
    driver.quit()
