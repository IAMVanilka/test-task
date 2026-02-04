from fastapi import APIRouter, HTTPException, Depends, Header

from modules.db.queryes import get_all_users, get_user_data, add_new_user, update_user_token, delete_user_data, update_user_data
from modules.secrets_manager import verify_password, generate_token
from models.pydantic_models import UserWithPassword, UserForRegistration, UserForUpdate
from models.response_models import BaseResponse, UserDataResponse, AuthorizationResponse, UserUpdateResponse
from models.db_models import UserRole

class RoleChecker:
    def __init__(self, allowed_roles: list[str]):
        self.allowed_roles = allowed_roles

    def __call__(self, x_api_token: str = Header(..., alias="x-api-token")):
        token = x_api_token
        if not token:
            raise HTTPException(status_code=401, detail="x-api-token is missing")

        user = get_user_data(token=token)
        if not user:
            raise HTTPException(
                status_code=403,
                detail="x-api-token is wrong!"
            )
        
        if user.role not in self.allowed_roles:
            raise HTTPException(
                status_code=403,
                detail="User doesn't have permissions to perform this action!"
            )

        return user.role


async def check_user_password(user_data: UserWithPassword) -> dict:
    user_db_data = get_user_data(username=user_data.username)
    if not user_db_data or not verify_password(user_data.password, user_db_data.password):
        raise HTTPException(
            status_code=403,
            detail="User doesn't exist or password is wrong!"
        )
 
    return user_db_data

main_router = APIRouter(prefix="/api/users", tags=['Управление пользователями'])
auth_router = APIRouter(prefix="/api/auth", tags=['Авторизация пользователей'])


# АВТОРИЗАЦИЯ
@auth_router.post(
    "",
    response_model=AuthorizationResponse,
    summary="Авторизация пользователя",
    description="Позволяет получить x-api-token через авторизацию комбинацией username+password.",
    responses={
        200: {"description": "Авторизация успешна."},
        403: {"description": "Неверный username или пароль."},
    }
)
async def authorization(user_data = Depends(check_user_password)):
    token = generate_token()
    success = update_user_token(token, user_data.username)
    if not success:
        raise HTTPException(status_code=500, detail="Database error!")
    else:
        return AuthorizationResponse(x_api_token=token)
    

# ОСНОВНЫЕ ЭНДПОИНТЫ
@main_router.get(
    "/get_list",
    dependencies=[Depends(RoleChecker(allowed_roles=["admin", "superadmin"]))],
    response_model=list[UserDataResponse],
    summary="Получить список пользователей",
    description="""
    Возвращает список пользователей с возможностью фильтрации и сортировки в query параметрах. 

    - Параметр limit ограничивает количество возвращаемых записей (макс. 100).
    - Параметр offset задаёт смещение для пагинации.
    - Параметр role фильтрует пользователей по роли.
    - Параметры order_by и order_desc позволяют сортировать результаты по id, username или role.
    - Требуется x-api-token в headers с правами 'admin' или 'superadmin'.
    """,
    responses={
        200: {"description": "Список данных сформирован успешно."},
        403: {"description": "Нет доступа (отсутствует верный x-api-token или недостаточно привелегий)."},
    }
)
async def get_list(limit: int = 100, offset: int = 0, role: UserRole = None, order_by: str = "id", order_desc: bool = False):
    users_list = get_all_users(limit=limit, offset=offset, role=role, order_by=order_by, order_desc=order_desc)
    return users_list

@main_router.get(
    "/get_user",
    summary="Получить данные пользователя",
    response_model=UserDataResponse,
    description="""
    Поиск пользователя по username.

    - Необхоодимо передать username в query-параметрах (Учитывая регистр).
    - Требуется любой x-api-token в headers.
    """,
    responses={
        200: {"description": "Пользователь найден."},
        403: {"description": "Нет доступа (отсутствует верный x-api-token)."},
        404: {"description": "Пользователь не найден."},
    }
)
async def get_user(username: str = None, user_role = Depends(RoleChecker(allowed_roles=["user", "admin", "superadmin"]))):
    user_data = get_user_data(username)

    if user_data is None:
        raise HTTPException(status_code=404, detail=f"User {user_data.username} not found!")
    return user_data

@main_router.post(
    "/add_new",
    response_model=BaseResponse,
    summary="Создать нового пользователя с ролью",
    description="""Регистрирует пользователя с указанной ролью. По умолчанию — 'user'.

    - Требуется x-api-token в headers с правами 'admin' или 'superadmin'.
    - Только 'superadmin' может создавать пользователей с ролью 'superadmin' или 'admin'.
    - Доступные роли: 'user', 'admin', 'superadmin'.
    """,
    responses={
        200: {"description": "Пользователь успешно создан"},
        403: {"description": "Нет доступа (отсутствует верный x-api-token или недостаточно привелегий)."},
    }
)
async def add_user(user_data: UserForRegistration, user_role = Depends(RoleChecker(allowed_roles=["admin", "superadmin"]))):
    if user_role == "admin" and user_data.role == "superadmin" or user_role == "admin" and user_data.role == "admin":
        raise HTTPException(status_code=403, detail="Admin can't create superadmin and admin users!")
    success = add_new_user(
        username=user_data.username,
        password=user_data.password,
        email=user_data.email,
        role=user_data.role
        )

    if success:
        return BaseResponse(
            msg=f"User {user_data.username} successfully added!"
        )
    else:
        raise HTTPException(status_code=500, detail="Database error!")
    
@main_router.delete(
    "/delete_user",
    response_model=BaseResponse,
    summary="Удалить пользователя.",
    description="""Удаляет пользователя по заданому username.

    - Требуется x-api-token в headers с правами 'admin' или 'superadmin'.
    - Только 'superadmin' может удалять пользователей с ролью 'superadmin' или 'admin'.
    """,
    responses={
    200: {"description": "Пользователь успешно удален"},
    403: {"description": "Нет доступа (отсутствует верный x-api-token или недостаточно привелегий)."},
    404: {"description": "Пользователь не найден."},
    }
)
async def delete_user(username: str, user_role = Depends(RoleChecker(allowed_roles=["admin", "superadmin"]))):
    if user_role == "admin":
        user_db_data = get_user_data(username=username)
        if user_db_data.role in ["admin", "superadmin"]:
            raise HTTPException(status_code=403, detail="Admin can't delete admin and superadmin users!")
    success = delete_user_data(username=username)

    if success:
        return BaseResponse(
            msg=f"User {username} successfully deleted!"
        )
    else:
        raise HTTPException(status_code=500, detail="Database error!")

@main_router.patch(
    "/edit_user",
    response_model=UserUpdateResponse,
    summary="Изменить данные пользователя",
    description=
    """Обновляет данные пользователя.

    - Требуется x-api-token в headers с правами 'admin' или 'superadmin'.
    - Только 'superadmin' может изменять пользователей с ролью 'superadmin' или 'admin'.
    """,
    responses={
    200: {"description": "Пользователь успешно изменен."},
    403: {"description": "Нет доступа (отсутствует верный x-api-token или недостаточно привелегий)."},
    404: {"description": "Пользователь не найден."}
    }
)
async def update_user(user_data: UserForUpdate, user_role = Depends(RoleChecker(allowed_roles=["admin", "superadmin"]))):
    if user_role == "admin" and user_data.role in ['admin', 'user']:
        raise HTTPException(status_code=403, detail="Only superadmin can update users with admin roles!")

    user_to_change = get_user_data(username=user_data.username)
    if user_to_change is None:
        raise HTTPException(status_code=404, detail=f"User {user_data.username} not found!")

    if user_to_change.role in ["admin", "superadmin"] and user_role == "admin":
        raise HTTPException(status_code=403, detail="Only superadmin can update users with admin roles!")
    
    success = update_user_data(
        user_data.username,
        user_data.new_username,
        user_data.email,
        user_data.role,
        user_data.password
        )
    
    user_to_change = get_user_data(username=user_data.new_username)

    if success:
        return UserUpdateResponse(
            msg="User successfully updated!",
            username=user_data.username,
            new_username=user_to_change.username,
            email=user_to_change.email,
            role=user_to_change.role,
        )
    else:
        raise HTTPException(status_code=500, detail="Database error!")