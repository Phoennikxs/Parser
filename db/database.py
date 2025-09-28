import mysql.connector
import pandas as pd

# Конфигурация подключения
DB_CONFIG = {
    'user': 'root',
    'password': 'cbvathjgjkm2020',
    'host': 'localhost',
    'database': 'detalisto',
    'port': 3306
}

# Функция подключения к базе данных и создания таблицы
def connect_db():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        create_table_if_not_exists(conn)
        return conn
    except mysql.connector.Error as e:
        print(f"Ошибка подключения к БД: {e}")
        return None

# Создание таблицы, если не существует
def create_table_if_not_exists(conn):
    try:
        cursor = conn.cursor()
        cursor.execute(''' 
            CREATE TABLE IF NOT EXISTS avito_items (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name TEXT NOT NULL,
                price INT NOT NULL,
                href TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()
    except mysql.connector.Error as e:
        print(f"Ошибка при создании таблицы: {e}")
    finally:
        try:
            cursor.close()
        except:
            pass

# Проверка на дубликат перед вставкой (учитываем name, price и href)
def check_if_exists(conn, name, price, href):
    try:
        cursor = conn.cursor()
        cursor.execute(''' 
            SELECT COUNT(*) FROM avito_items WHERE name = %s AND price = %s AND (href = %s OR (href IS NULL AND %s IS NULL))
        ''', (name, price, href, href))
        count = cursor.fetchone()[0]
        return count > 0  # Возвращает True, если запись уже существует
    except mysql.connector.Error as e:
        print(f"Ошибка при проверке дубликатов: {e}")
        return False
    finally:
        try:
            cursor.close()
        except:
            pass

# Вставка данных с проверкой на дубликаты
def insert_into_db(name, price, href=None):
    conn = connect_db()
    if not conn:
        return

    try:
        if check_if_exists(conn, name, price, href):
            print(f"Дубликат найден: {name}, {price}, {href}. Запись не добавлена.")
            return

        cursor = conn.cursor()
        cursor.execute(''' 
            INSERT INTO avito_items (name, price, href) 
            VALUES (%s, %s, %s)
        ''', (name, price, href))
        conn.commit()
        print(f"Запись добавлена: {name}, {price}, {href}")
    except mysql.connector.Error as e:
        print(f"Ошибка при вставке данных: {e}")
    finally:
        try:
            cursor.close()
        except:
            pass
        try:
            conn.close()
        except:
            pass

# Экспорт данных из базы в Excel
def export_to_excel():
    try:
        conn = connect_db()
        if conn:
            query = "SELECT id, name, price, href, created_at FROM avito_items"
            # pd.read_sql может работать с mysql-connector подключением
            df = pd.read_sql(query, conn)
            df.to_excel("avito_items.xlsx", index=False, engine='openpyxl')
            print("Данные успешно экспортированы в avito_items.xlsx")
            conn.close()
    except Exception as e:
        print(f"Ошибка при экспорте данных в Excel: {e}")

# Пример использования
if __name__ == "__main__":
    # Пример вставки (замените title, price, href на реальные переменные из вашего парсера)
    # insert_into_db(title, price, href)

    # Экспорт данных в Excel
    export_to_excel()
