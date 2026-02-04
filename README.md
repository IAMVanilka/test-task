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
```http
http://<ваш url>:8000/docs
```
Если открылась документация **Swagger UI** — всё работает корректно.

# Аутентификация

1. Отправьте **POST-запрос** на эндпоинт:
```http
POST http://localhost:8000/api/auth
```

2. В теле запроса (**request body**) укажите логин и пароль в формате JSON:
```json
{
  "username": "ваш_логин",
  "password": "ваш_пароль"
}
```
*(Значения должны совпадать с `SUPER_ADMIN_USERNAME` и `SUPER_ADMIN_PASSWORD`, заданными в `docker-compose.yaml`.)*

3. В ответе вы получите заголовок `x-api-token`.

4. Для всех последующих запросов добавляйте этот токен в заголовки
```http
x-api-token: <полученный_токен>
```

Теперь вы можете выполнять любые API-запросы.

**Так же для удобства я собрал [Postman Collection](https://www.postman.com/altimetry-observer-62324961/vanilka-s-workspace/collection/36019807-837f58bd-e071-460a-8829-b71b31cc3463)**
