from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import time
import re
import json

# Настройка Chrome
chrome_options = Options()
chrome_options.add_argument("--headless")  # без GUI
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

service = Service(r"C:\Users\phoen\PycharmProjects\PythonProject\chromedriver-win64\chromedriver.exe")
driver = webdriver.Chrome(service=service, options=chrome_options)

# Ссылка на запчасти для ТО в Таганроге
url = "https://baza.drom.ru/taganrog/sell_spare_parts/+/%E7%E0%EF%F7%E0%F1%F2%E8+%E4%EB%FF+%D2%CE/"
driver.get(url)

wait = WebDriverWait(driver, 15)

# Сколько объявлений хотим собрать
target_count = 50  # <-- сюда ставим нужное количество
collected = []
i = 0

SCROLL_PAUSE_TIME = 2

while len(collected) < target_count:
    # Находим все текущие объявления
    items = driver.find_elements(By.XPATH, "//*[contains(@class, 'bull-list-item-js -exact')]")

    for item in items[len(collected):]:  # берём только новые
        try:
            title_element = WebDriverWait(item, 3).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '[data-role="bulletin-link"]'))
            )
            title = title_element.text
        except TimeoutException:
            title = None

        try:
            price_element = WebDriverWait(item, 3).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '[data-role="price"]'))
            )
            raw_price = price_element.text
            price_digits = re.sub(r'\D', '', raw_price)
            price = int(price_digits) if price_digits else 0
        except TimeoutException:
            price = 0

        collected.append({"title": title, "price": price})

        to_json = {'name': title, 'price': price, "id": 1}

        with open(f"object{i}.json", "w", encoding="utf-8") as f:
            json.dump(to_json, f, ensure_ascii=False, indent=2)
        i += 1
        if len(collected) >= target_count:
            break

    # Скроллим вниз для подгрузки новых объявлений
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(SCROLL_PAUSE_TIME)

driver.quit()
print(f"Собрано объявлений: {len(collected)}")
