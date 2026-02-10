from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.exc import IntegrityError

from models.db_models import UsersOrm
from modules.db.database import engine
from modules.secrets_manager import hash_password

session_factory = async_sessionmaker(engine)


async def get_all_users(
    limit: int = 100,
    offset: int = 0,
    role: str = None,
    order_by: str = "id",
    order_desc: bool = False,
) -> list[dict]:
    async with session_factory() as session:
        columns = [col for col in UsersOrm.__table__.columns if col.name != 'password']
        stmt = select(*columns)

        if role is not None:
            stmt = stmt.where(UsersOrm.role == role)

        limit = min(limit, 100)

        order_col = UsersOrm.id
        if order_by == "username":
            order_col = UsersOrm.username
        elif order_by == "role":
            order_col = UsersOrm.role

        stmt = stmt.order_by(order_col.desc() if order_desc else order_col)
        stmt = stmt.offset(offset).limit(limit)

        result = await session.execute(stmt)
        return [row._asdict() for row in result.fetchall()]
    
async def get_user_data(username: str = None, token: str = None) -> UsersOrm | None:
    async with session_factory() as session:
        if username:
            stmt = select(UsersOrm).where(UsersOrm.username == username)
        elif token:
            stmt = select(UsersOrm).where(UsersOrm.token == token)
        else:
            raise AttributeError("Необходимо указать username или token для поиска пользователя!")

        user = (await session.execute(stmt)).scalar_one_or_none()

        return user
    
async def add_new_user(username: str, password: str, role: str, email: str = None) -> bool:
    async with session_factory() as session:
        session.add(
            UsersOrm(
                username=username,
                email=email,
                role=role,
                password=hash_password(password)
            )
        )
        await session.commit()

        return True
    
async def update_user_token(token: str, username: str) -> bool:
    async with session_factory() as session:
        stmt = update(UsersOrm).filter(UsersOrm.username == username).values(
            token=token
        )
        await session.execute(stmt)
        await session.commit()

    return True

async def delete_user_data(username: str) -> bool:
    async with session_factory() as session:
        stmt = select(UsersOrm).where(UsersOrm.username == username)
        user = (await session.execute(stmt)).scalar_one_or_none()
        if user:
            await session.delete(user)
            await session.commit()
            return True
        else:
            return False

async def update_user_data(
    username: str,
    new_username: str | None = None,
    email: str | None = None,
    role: str | None = None,
    password: str | None = None
) -> bool:
    async with session_factory() as session:
        stmt = select(UsersOrm).where(UsersOrm.username == username)
        user = (await session.execute(stmt)).scalar_one_or_none()
        
        if not user:
            return False

        update_data = {}
        if new_username is not None:
            update_data["username"] = new_username
        if email is not None:
            update_data["email"] = email
        if role is not None:
            update_data["role"] = role
        if password is not None:
            update_data["password"] = hash_password(password)

        if not update_data:
            return True

        try:
            for key, value in update_data.items():
                setattr(user, key, value)
            await session.commit()
            return True
        except IntegrityError:
            await session.rollback()
            return False