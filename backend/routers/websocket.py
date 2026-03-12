from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from services.websocket_manager import manager
from services.store import get_recent_arcs, get_attack_stats
import json

router = APIRouter()


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        arcs = get_recent_arcs(50)
        stats = get_attack_stats()

        await manager.send_personal(websocket, {
            "type": "init",
            "data": {
                "arcs": [arc.model_dump(mode="json") for arc in arcs],
                "stats": stats.model_dump(mode="json"),
            },
        })

        while True:
            data = await websocket.receive_text()
            msg = json.loads(data)
            if msg.get("type") == "ping":
                # Send fresh stats on every ping
                stats = get_attack_stats()
                await manager.send_personal(websocket, {"type": "pong"})
                await manager.send_personal(websocket, {
                    "type": "stats_refresh",
                    "data": stats.model_dump(mode="json"),
                })

    except WebSocketDisconnect:
        manager.disconnect(websocket)