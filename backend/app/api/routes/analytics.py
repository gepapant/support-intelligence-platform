from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    status,
)
from sqlalchemy.orm import Session

from app.api.dependencies.auth import (
    require_admin,
)
from app.db.session import get_db
from app.repositories.analytics import (
    AnalyticsRepository,
)
from app.schemas.analytics import (
    AnalyticsSummary,
    AnalyticsTrends,
)
from app.services.analytics import (
    AnalyticsService,
)

router = APIRouter(
    prefix="/analytics",
    tags=["Analytics"],
    dependencies=[
        Depends(require_admin),
    ],
)


def get_analytics_service(
    db: Session = Depends(get_db),
) -> AnalyticsService:
    return AnalyticsService(repository=AnalyticsRepository(db))


@router.get(
    "/summary",
    response_model=AnalyticsSummary,
)
def get_analytics_summary(
    service: AnalyticsService = Depends(get_analytics_service),
):
    return service.get_summary()


@router.get(
    "/trends",
    response_model=AnalyticsTrends,
)
def get_analytics_trends(
    days: int = Query(
        default=7,
    ),
    service: AnalyticsService = Depends(get_analytics_service),
):
    if days not in {7, 30}:
        raise HTTPException(
            status_code=(status.HTTP_422_UNPROCESSABLE_ENTITY),
            detail=("days must be either 7 or 30"),
        )

    return service.get_trends(days)
