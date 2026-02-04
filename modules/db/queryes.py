from sqlalchemy import select, update
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError

from models.db_models import UsersOrm
from modules.db.database import engine
from modules.secrets_manager import hash_password

session_factory = sessionmaker(engine)


def get_all_users(
    limit: int = 100,
    offset: int = 0,
    role: str = None,
    order_by: str = "id",
    order_desc: bool = False,
) -> list[dict]:
    with session_factory() as session:
        query = session.query(*[col for col in UsersOrm.__table__.columns if col.name != 'password'])

        if role is not None:
            query = query.filter(UsersOrm.role == role)

        limit = min(limit, 100)

        if order_by == "id":
            order_col = UsersOrm.id
        elif order_by == "username":
            order_col = UsersOrm.username
        elif order_by == "role":
            order_col = UsersOrm.role
        else:
            order_col = UsersOrm.id

        query = query.order_by(order_col.desc() if order_desc else order_col)
        query = query.offset(offset).limit(limit)

        return [row._asdict() for row in query.all()]
    
def get_user_data(username: str = None, token: str = None) -> UsersOrm | None:
    with session_factory() as session:
        if username:
            stmt = select(UsersOrm).where(UsersOrm.username == username)
        elif token:
            stmt = select(UsersOrm).where(UsersOrm.token == token)
        else:
            raise AttributeError("Необходимо указать username или token для поиска пользователя!")

        result = session.execute(stmt).scalar_one_or_none()

        return result
    
def add_new_user(username: str, password: str, role: str, email: str = None) -> bool:
    with session_factory() as session:
        session.add(
            UsersOrm(
                username=username,
                email=email,
                role=role,
                password=hash_password(password)
            )
        )
        session.commit()

        return True
    
def update_user_token(token: str, username: str) -> bool:
    with session_factory() as session:
        stmt = update(UsersOrm).filter(UsersOrm.username == username).values(
            token=token
        )
        session.execute(stmt)
        session.commit()

    return True

def delete_user_data(username: str) -> bool:
    with session_factory() as session:
        stmt = select(UsersOrm).where(UsersOrm.username == username)
        user = session.execute(stmt).scalar_one_or_none()
        if user:
            session.delete(user)
            session.commit()
            return True
        return False

def update_user_data(
    username: str,
    new_username: str | None = None,
    email: str | None = None,
    role: str | None = None,
    password: str | None = None
) -> bool:
    with session_factory() as session:
        stmt = select(UsersOrm).where(UsersOrm.username == username)
        user = session.execute(stmt).scalar_one_or_none()
        
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
            session.commit()
            return True
        except IntegrityError:
            session.rollback()
            return False