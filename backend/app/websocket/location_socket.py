import json
import logging
from datetime import datetime, timezone
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from app.websocket.manager import ws_manager
from app.config.database import SessionLocal
from app.models.location import Location
from app.models.child import Child
from app.schemas.location import LocationCreate
from app.services.location_service import location_service
from app.config.security import decode_access_token

logger = logging.getLogger("safety.location_socket")
router = APIRouter(tags=["Safety WebSocket"])

@router.websocket("/ws/location/{child_id}")
async def live_location_stream(
    websocket: WebSocket,
    child_id: str,
    token: str = Query(None)
):
    """
    WebSocket endpoint for real-time live location tracking and streaming.
    Caregiver app connects to listen to child location updates or ingest live pings.
    """
    user_id = None
    if token:
        user_id = decode_access_token(token)

    await ws_manager.connect_tracker(child_id, websocket, user_id)
    db = SessionLocal()

    try:
        # Send initial latest location upon connection
        latest_loc = (
            db.query(Location)
            .filter(Location.child_id == child_id)
            .order_by(Location.created_at.desc())
            .first()
        )
        if latest_loc:
            await websocket.send_json({
                "type": "INITIAL_LOCATION",
                "child_id": child_id,
                "latitude": latest_loc.latitude,
                "longitude": latest_loc.longitude,
                "accuracy": latest_loc.accuracy,
                "speed": latest_loc.speed,
                "heading": latest_loc.heading,
                "recorded_at": latest_loc.recorded_at.isoformat() if latest_loc.recorded_at else None,
            })

        while True:
            data = await websocket.receive_text()
            message = json.loads(data)

            # If client is sending a location ping (e.g. tracking device stream)
            if message.get("type") == "PING_LOCATION":
                loc_in = LocationCreate(
                    child_id=child_id,
                    device_id=message.get("device_id"),
                    latitude=float(message["latitude"]),
                    longitude=float(message["longitude"]),
                    accuracy=float(message.get("accuracy", 5.0)),
                    speed=float(message.get("speed", 0.0)),
                    heading=float(message.get("heading", 0.0)),
                    battery_level=float(message.get("battery_level", 100)),
                    address=message.get("address"),
                )
                res = location_service.record_location(db, loc_in, evaluate_geofence=True)
                loc_obj = res["location"]

                broadcast_payload = {
                    "type": "LOCATION_UPDATE",
                    "child_id": child_id,
                    "latitude": loc_obj.latitude,
                    "longitude": loc_obj.longitude,
                    "accuracy": loc_obj.accuracy,
                    "speed": loc_obj.speed,
                    "heading": loc_obj.heading,
                    "battery_level": loc_obj.battery_level,
                    "geofence_status": res.get("geofence_evaluation"),
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                }
                await ws_manager.broadcast_to_child_trackers(child_id, broadcast_payload)

            elif message.get("type") == "HEARTBEAT":
                await websocket.send_json({"type": "PONG", "timestamp": datetime.now(timezone.utc).isoformat()})

    except WebSocketDisconnect:
        ws_manager.disconnect_tracker(child_id, websocket, user_id)
    except Exception as e:
        logger.error(f"WebSocket error in live_location_stream: {e}")
        ws_manager.disconnect_tracker(child_id, websocket, user_id)
    finally:
        db.close()
