import uuid

from fastapi import (
    APIRouter,
    Depends,
    Query,
    Response,
    status,
)
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import (
    CurrentUser,
    get_current_user,
    require_admin,
)
from app.db.database import get_db
from app.repositories.article import ArticleRepository
from app.repositories.category import CategoryRepository
from app.repositories.topic import TopicRepository
from app.schemas.article import (
    ArticleCreate,
    ArticleResponse,
    ArticleUpdate,
)
from app.services.article import ArticleService


router = APIRouter(
    tags=["Articles"],
)


def get_article_service(
    db: AsyncSession,
) -> ArticleService:
    return ArticleService(
        ArticleRepository(db),
        CategoryRepository(db),
        TopicRepository(db),
    )


@router.get(
    "/articles",
    response_model=list[ArticleResponse],
)
async def get_articles(
    category: str | None = None,
    search: str | None = None,
    limit: int = Query(
        default=20,
        ge=1,
        le=100,
    ),
    offset: int = Query(
        default=0,
        ge=0,
    ),
    current_user: CurrentUser = Depends(
        get_current_user
    ),
    db: AsyncSession = Depends(get_db),
):
    service = get_article_service(db)

    return await service.get_all(
        current_user=current_user,
        category=category,
        search=search,
        limit=limit,
        offset=offset,
    )


@router.get(
    "/articles/{slug}",
    response_model=ArticleResponse,
)
async def get_article(
    slug: str,
    current_user: CurrentUser = Depends(
        get_current_user
    ),
    db: AsyncSession = Depends(get_db),
):
    service = get_article_service(db)

    return await service.get_by_slug(
        slug,
        current_user,
    )


@router.post(
    "/topics/{topic_id}/articles",
    response_model=ArticleResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_article(
    topic_id: uuid.UUID,
    data: ArticleCreate,
    _: CurrentUser = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    service = get_article_service(db)

    return await service.create(
        topic_id,
        data,
    )


@router.patch(
    "/articles/{article_id}",
    response_model=ArticleResponse,
)
async def update_article(
    article_id: uuid.UUID,
    data: ArticleUpdate,
    _: CurrentUser = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    service = get_article_service(db)

    return await service.update(
        article_id,
        data,
    )


@router.delete(
    "/articles/{article_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_article(
    article_id: uuid.UUID,
    _: CurrentUser = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    service = get_article_service(db)

    await service.delete(article_id)

    return Response(
        status_code=status.HTTP_204_NO_CONTENT
    )