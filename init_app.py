import os

from modules.db.database import create_tables
from modules.db.queryes import add_new_user, get_user_data

def initialize_app():
    try:
        create_tables()

        SUPER_ADMIN_USERNAME = os.getenv("SUPER_ADMIN_USERNAME")
        SUPER_ADMIN_PASSWORD = os.getenv("SUPER_ADMIN_PASSWORD")

        if not SUPER_ADMIN_USERNAME or not SUPER_ADMIN_PASSWORD:
            print("Ошибка: SUPER_ADMIN_USERNAME и SUPER_ADMIN_PASSWORD должны быть заданы!")
            return

        user_data = get_user_data(SUPER_ADMIN_USERNAME)
        if user_data and user_data.role == "superadmin":
            return

        add_new_user(
            username=SUPER_ADMIN_USERNAME,
            password=SUPER_ADMIN_PASSWORD,
            role="superadmin"
        )
        print(f"Суперадмин '{SUPER_ADMIN_USERNAME}' успешно создан.")

    except Exception as e:
        print("ОШИБКА СОЗДАНИЯ СУПЕРАДМИНА В БАЗЕ ДАННЫХ! Текст ошибки: \n", e)

if __name__ == "__main__":
    initialize_app()