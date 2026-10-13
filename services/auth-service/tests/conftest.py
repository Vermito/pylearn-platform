import asyncio

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.core.config import settings
from app.core.security import create_access_token, hash_password
from app.db.base import Base
from app.db.database import get_db
from app.main import app
from app.models.user import User


# ==========================================================
# Event loop
#
# ОДИН на всю сессию тестирования.
# Без этого pytest-asyncio создаёт новый loop для каждого
# теста, и engine (созданный один раз) падает с ошибкой
# "got Future attached to a different loop".
# ==========================================================

@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


# ==========================================================
# Engine
#
# Создаётся ВНУТРИ session-scoped loop, а не при импорте
# модуля. Это ключевое отличие от прежней версии.
# ==========================================================

@pytest_asyncio.fixture(scope="session")
async def test_engine():
    engine = create_async_engine(
        settings.test_database_url,
        echo=False,
    )
    yield engine
    await engine.dispose()


@pytest_asyncio.fixture(scope="session")
def test_session_factory(test_engine):
    return async_sessionmaker(
        bind=test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )


@pytest_asyncio.fixture(scope="session", autouse=True)
async def prepare_database(test_engine):
    async with test_engine.begin() as connection:
        await connection.run_sync(Base.metadata.drop_all)
        await connection.run_sync(Base.metadata.create_all)

    yield

    async with test_engine.begin() as connection:
        await connection.run_sync(Base.metadata.drop_all)


# ==========================================================
# Изоляция каждого теста через транзакцию
#
# Перед тестом открываем connection, начинаем транзакцию,
# подменяем get_db так, чтобы он использовал эту транзакцию.
# После теста — откат.
# ==========================================================

@pytest_asyncio.fixture(autouse=True)
async def db_transaction(test_engine):
    """
    Обёртка для каждого теста: открывает транзакцию,
    откатывает после завершения.
    """
    async with test_engine.connect() as connection:
        trans = await connection.begin()

        # Создаём сессию, привязанную к этой connection
        session_factory = async_sessionmaker(
            bind=connection,
            class_=AsyncSession,
            expire_on_commit=False,
            join_transaction_mode="create_savepoint",
        )

        async def _override_get_db():
            async with session_factory() as session:
                yield session

        # Запоминаем старый override и ставим новый
        old_override = app.dependency_overrides.get(get_db)
        app.dependency_overrides[get_db] = _override_get_db

        yield

        # Возвращаем старый override
        if old_override is not None:
            app.dependency_overrides[get_db] = old_override
        else:
            app.dependency_overrides.pop(get_db, None)

        # Откат транзакции
        await trans.rollback()


# ==========================================================
# HTTP-клиент
# ==========================================================

@pytest_asyncio.fixture
async def client():
    transport = ASGITransport(app=app)

    async with AsyncClient(
        transport=transport,
        base_url="http://test",
    ) as test_client:
        yield test_client


# ==========================================================
# Пользователи
#
# Используют ту же session_factory, что и db_transaction,
# чтобы попадать в транзакцию текущего теста.
# ==========================================================

@pytest_asyncio.fixture
async def regular_user(db_transaction, test_session_factory):
    async with test_session_factory() as session:
        user = User(
            username="regular",
            email="regular@example.com",
            password_hash=hash_password(
                "RegularPassword123"
            ),
            role="user",
        )

        session.add(user)

        await session.commit()
        await session.refresh(user)

        return user


@pytest_asyncio.fixture
async def user_token(regular_user):
    return create_access_token(
        subject=str(regular_user.id),
        role=regular_user.role,
    )


@pytest_asyncio.fixture
async def admin_user(db_transaction, test_session_factory):
    async with test_session_factory() as session:
        admin = User(
            username="admin",
            email="admin@example.com",
            password_hash=hash_password(
                "AdminPassword123"
            ),
            role="admin",
        )

        session.add(admin)

        await session.commit()
        await session.refresh(admin)

        return admin


@pytest_asyncio.fixture
async def admin_token(admin_user):
    return create_access_token(
        subject=str(admin_user.id),
        role=admin_user.role,
    )