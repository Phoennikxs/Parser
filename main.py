from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import time
import psycopg2
import json
import re

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
chrome_options.add_argument("--disable-webgl")  # Отключает WebGL
chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36")



# Указываем путь к драйверу Chrome
service = Service(r"C:\Users\phoen\PycharmProjects\PythonProject\chromedriver-win64\chromedriver.exe")
driver = webdriver.Chrome(service=service, options=chrome_options)

BASE_URL = "https://www.avito.ru/taganrog/zapchasti_i_aksessuary/zapchasti_i_aksessuary/zapchasti_dlya_to-ASgBAgICAUSsvhPw_I0D?cd=1"
MAX_PAGES = 2  # Ограничение на количество страниц
i = 0
for page in range(1, MAX_PAGES + 1):
    url = f"{BASE_URL}?p={page}"
    driver.get(url)
    time.sleep(5)

    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//*[contains(@class, 'iva-item-root')]")
        ))
    except Exception as e:
        print(f"Страница {page} не загрузилась, пропускаем...")
        continue

    # Получаем список объявлений
    items = driver.find_elements(By.XPATH, "//*[contains(@class, 'iva-item-root')]")

    if not items:
        print(f"На странице {page} объявлений не найдено, заканчиваем парсинг.")
        break

    for item in items:
        try:
            title_element = WebDriverWait(item, 3).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '[data-marker="item-title"] h3'))
            )
            title = title_element.text


        except TimeoutException:
            title = None

        try:
            price_element = WebDriverWait(item, 3).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '[data-marker="item-price"]'))
            )
            raw_price = price_element.text
            price_digits = re.sub(r'\D', '', raw_price)
            price = int(price_digits) if price_digits else 0


        except TimeoutException:
            price = 0

        to_json = {'name':title, 'price':price, "id":3}

        with open(f"object{i}.json", "w", encoding="utf-8") as f:
            json.dump(to_json, f, ensure_ascii=False, indent=2)

        i += 1

# Закрываем браузер
driver.quit()

