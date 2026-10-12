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

test_engine = create_async_engine(
    settings.test_database_url,
    echo=False,
)

TestSessionLocal = async_sessionmaker(
    bind=test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def override_get_db():
    async with TestSessionLocal() as session:
        yield session


app.dependency_overrides[get_db] = override_get_db


@pytest_asyncio.fixture(autouse=True)
async def prepare_database():
    async with test_engine.begin() as connection:
        await connection.run_sync(Base.metadata.drop_all)
        await connection.run_sync(Base.metadata.create_all)

    yield

    async with test_engine.begin() as connection:
        await connection.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def client():
    transport = ASGITransport(app=app)

    async with AsyncClient(
        transport=transport,
        base_url="http://test",
    ) as test_client:
        yield test_client


@pytest_asyncio.fixture
async def regular_user():
    async with TestSessionLocal() as session:
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
async def admin_user():
    async with TestSessionLocal() as session:
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