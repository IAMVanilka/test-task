# Инструкция для запуска проекта

1. Клонируйте данный репозиторий
```bash
git clone https://github.com/IAMVanilka/test-task
cd test-task
```

2. Откройте `docker-compose.yaml` и задать в переменных окружения имя супер-администратора `SUPER_ADMIN_USERNAME` и пароль `SUPER_ADMIN_PASSWORD`.
```yaml
environment:
  - SUPER_ADMIN_USERNAME: ваш_логин
  - SUPER_ADMIN_PASSWORD: ваш_пароль
```

3. Запустите сборку и запуск контейнера
```bash
docker compose up --build
```

4. (Опционально) Настройте reverse proxy через Nginx или Apache, если требуется:
- проксирование с домена,
- поддержка HTTPS,

5. Проверьте работоспособность:
**Откройте в браузере:**
```
http://<ваш url>:8000/docs
```
Если открылась документация **Swagger UI** — всё работает корректно.