import asyncio
import logging
from config import get_settings
from services.abuseipdb import fetch_blacklisted_ips, build_attack_events
from services.store import ingest_attack_events
from services.websocket_manager import manager

logger = logging.getLogger(__name__)
settings = get_settings()

_scheduler_task: asyncio.Task | None = None


async def poll_attacks():
    logger.info("Attack poller started")
    while True:
        try:
            logger.info("Fetching IPs from AbuseIPDB...")
            raw_ips = await fetch_blacklisted_ips()
            events = await build_attack_events(raw_ips)
            new_arcs = ingest_attack_events(events)

            if new_arcs:
                logger.info(f"New arcs: {len(new_arcs)} — broadcasting")
                for arc in new_arcs:
                    await manager.broadcast({
                        "type": "new_arc",
                        "data": arc.model_dump(mode="json"),
                    })

            await manager.broadcast({
                "type": "stats_update",
                "data": {"new_count": len(new_arcs)},
            })

        except Exception as e:
            logger.error(f"Poll error: {e}")

        await asyncio.sleep(settings.ATTACK_POLL_INTERVAL)


async def start_scheduler():
    global _scheduler_task
    _scheduler_task = asyncio.create_task(poll_attacks())
    logger.info("Scheduler started")


async def stop_scheduler():
    global _scheduler_task
    if _scheduler_task:
        _scheduler_task.cancel()
        try:
            await _scheduler_task
        except asyncio.CancelledError:
            pass
    logger.info("Scheduler stopped")