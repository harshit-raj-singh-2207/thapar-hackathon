from fastapi import APIRouter
from app.api.v1.auth.router import router as auth_router
from app.api.v1.caregivers.router import router as caregivers_router
from app.api.v1.community.media_routes import router as media_router
from app.api.v1.community.chat_routes import router as chat_router
from app.api.v1.community.group_routes import router as group_router
from app.api.v1.community.post_routes import router as post_router
from app.api.v1.community.comment_routes import router as comment_router
from app.api.v1.community.report_routes import router as report_router
from app.api.v1.community.resource_routes import router as resource_router
from app.api.v1.community.notification_routes import router as notification_router
from app.api.v1.support.router import router as support_router
from app.realtime.websocket_routes import router as ws_router

from app.api.v1.community.sound_routes import router as sound_router
from app.api.v1.community.social_routes import router as social_router
from app.api.v1.dashboard.router import router as dashboard_router

from app.routers.safety import router as safety_router
from app.websocket.location_socket import router as location_ws_router
from app.api.v1.communication.router import router as communication_router
from app.api.v1.learning.router import router as learning_router
from app.domains.safety.caregiver_dashboard_router import router as caregiver_dashboard_router

router = APIRouter()

router.include_router(dashboard_router)
router.include_router(caregiver_dashboard_router)
router.include_router(auth_router)
router.include_router(caregivers_router)
router.include_router(communication_router)
router.include_router(learning_router)
router.include_router(media_router)
router.include_router(chat_router)
router.include_router(group_router)
router.include_router(post_router)
router.include_router(comment_router)
router.include_router(resource_router)
router.include_router(report_router)
router.include_router(notification_router)
router.include_router(support_router)
router.include_router(sound_router)
router.include_router(social_router)
router.include_router(safety_router)
router.include_router(location_ws_router)
router.include_router(ws_router)


