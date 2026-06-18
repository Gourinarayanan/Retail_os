"""
RetailWise AI — Agents Router
POST /api/run-briefing   — SSE stream of the 7-agent pipeline (real-time via asyncio.Queue)
GET  /api/agent-status   — agent_log from the most recent run
"""

import asyncio
import json
import logging
from datetime import date

from fastapi import APIRouter
from sse_starlette.sse import EventSourceResponse

from agents.ceo_agent import run_pipeline_streaming
from database.db import SessionLocal
from database.models import DailyBriefing

router = APIRouter(prefix="/api", tags=["agents"])
logger = logging.getLogger(__name__)

# In-memory: agent_log from last completed pipeline run (for /agent-status)
_last_agent_log: list[dict] = []
_last_final_state: dict = {}


@router.post("/run-briefing")
async def run_briefing():
    """
    Run the full 7-agent pipeline. Streams real-time progress via SSE.

    Architecture:
      1. asyncio.Queue is created.
      2. run_pipeline_streaming(queue) is launched as a background task.
         Each agent puts its agent_log entries into the queue as they fire.
      3. This SSE generator reads from the queue and emits each entry
         immediately — no buffering at the end.
      4. When the pipeline puts None into the queue, the stream closes.

    Frontend connects with:
      const es = new EventSource('/api/run-briefing', {method: 'POST'})
      es.addEventListener('agent_update', e => console.log(JSON.parse(e.data)))
      es.addEventListener('complete', e => es.close())
    """
    global _last_agent_log, _last_final_state

    # One queue per request — isolates concurrent runs
    queue: asyncio.Queue = asyncio.Queue()

    # Launch pipeline as a background task so SSE generator can read from
    # the queue while the pipeline is still running
    pipeline_task = asyncio.create_task(_run_pipeline_task(queue))

    async def event_generator():
        global _last_agent_log, _last_final_state

        try:
            while True:
                # Block until the next entry (or sentinel None) is available
                try:
                    entry = await asyncio.wait_for(queue.get(), timeout=60.0)
                except asyncio.TimeoutError:
                    # Safety net: pipeline stalled
                    logger.error("[SSE] Queue read timed out after 60s.")
                    yield {
                        "event": "agent_update",
                        "data": json.dumps({
                            "agent": "ceo",
                            "status": "error",
                            "summary": "Pipeline timed out. Check server logs.",
                        }),
                    }
                    break

                # Sentinel — pipeline is done
                if entry is None:
                    break

                # Emit each agent_log entry as an SSE event
                yield {
                    "event": "agent_update",
                    "data": json.dumps(entry, default=str),
                }

        finally:
            # Wait for the pipeline task to finish (it may have already)
            final_state = await pipeline_task

            # Cache for /agent-status
            if final_state:
                _last_agent_log = final_state.get("agent_log", [])
                _last_final_state = final_state

            # Emit terminal "complete" event
            brief = final_state.get("daily_brief", "") if final_state else ""
            yield {
                "event": "complete",
                "data": json.dumps({
                    "run_id": final_state.get("run_id", "") if final_state else "",
                    "brief_preview": brief[:200] if brief else "",
                    "orders_count": len(final_state.get("orders_draft", [])) if final_state else 0,
                    "opportunities_count": len(final_state.get("opportunities", [])) if final_state else 0,
                    "sources": final_state.get("sources", []) if final_state else [],
                }),
            }

    return EventSourceResponse(event_generator())


async def _run_pipeline_task(queue: asyncio.Queue) -> dict | None:
    """
    Wrapper that runs run_pipeline_streaming() and returns the final state.
    Catches all exceptions so SSE generator always gets a sentinel.
    """
    try:
        return await run_pipeline_streaming(queue)
    except Exception as exc:
        logger.error("[SSE] Pipeline task crashed: %s", exc)
        # Ensure the SSE generator isn't left waiting forever
        await queue.put({
            "agent": "ceo",
            "status": "error",
            "summary": f"Pipeline crashed: {exc}",
        })
        await queue.put(None)   # sentinel
        return None


@router.get("/agent-status")
def get_agent_status():
    """
    Return the agent_log from the most recent pipeline run.
    Used by the frontend Agent Status panel between runs.
    """
    if not _last_agent_log:
        db = SessionLocal()
        try:
            briefing = (
                db.query(DailyBriefing)
                .filter(DailyBriefing.date == date.today())
                .first()
            )
            if briefing:
                return {
                    "date": briefing.date.isoformat(),
                    "agent_log": [],
                    "message": (
                        "Briefing exists for today but live log is not in memory. "
                        "Re-run to see real-time agent status."
                    ),
                }
        finally:
            db.close()

        return {
            "agent_log": [],
            "message": "No pipeline run yet today. Click 'Run Morning Briefing'.",
        }

    return {
        "agent_log": _last_agent_log,
        "run_id": _last_final_state.get("run_id", ""),
        "date": _last_final_state.get("date", ""),
    }
