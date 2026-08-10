from fastapi import APIRouter

from app.api.v1.endpoints.auth import router as auth_router
from app.api.v1.endpoints.birth_profiles import router as birth_profiles_router
from app.api.v1.endpoints.birth_time import router as birth_time_router
from app.api.v1.endpoints.interpretation import router as interpretation_router
from app.api.v1.endpoints.natal_chart import router as natal_chart_router
from app.api.v1.endpoints.notifications import router as notifications_router
from app.api.v1.endpoints.persisted_charts import router as persisted_charts_router
from app.api.v1.endpoints.social import router as social_router
from app.api.v1.endpoints.sun_sign import router as sun_sign_router

router = APIRouter()
router.include_router(auth_router, tags=["authentication"])
router.include_router(birth_profiles_router, tags=["birth profiles"])
router.include_router(persisted_charts_router, tags=["natal charts"])
router.include_router(sun_sign_router, prefix="/astrology", tags=["astrology"])
router.include_router(birth_time_router, prefix="/astrology", tags=["astrology"])
router.include_router(natal_chart_router, prefix="/astrology", tags=["astrology"])
router.include_router(interpretation_router, prefix="/athena", tags=["athena"])
router.include_router(social_router, tags=["social"])
router.include_router(notifications_router, tags=["notifications"])
