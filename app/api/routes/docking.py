from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import asyncio
import json
from celery.result import AsyncResult
from app.workers.celery_app import celery_app

router = APIRouter(prefix="/api/docking", tags=["docking"])

class DockRequest(BaseModel):
    smiles: str
    pdb_id: str
    exhaustiveness: int = 8

class TaskResponse(BaseModel):
    task_id: str
    status: str
    message: str

@router.post("/submit", response_model=TaskResponse)
async def submit_docking(req: DockRequest):
    # ارسال تسک با اسم (بدون ایمپورت کردن کدهای سنگین meeko)
    task = celery_app.send_task(
        "dock_ligand",
        kwargs={
            "smiles": req.smiles,
            "pdb_id": req.pdb_id,
            "exhaustiveness": req.exhaustiveness,
        },
        queue="docking",
    )
    return TaskResponse(
        task_id=task.id,
        status="submitted",
        message=f"Poll /api/docking/{task.id} or use SSE at /api/docking/{task.id}/stream",
    )

@router.get("/{task_id}")
async def get_docking_status(task_id: str):
    # گرفتن نتیجه با استفاده از AsyncResult
    task = AsyncResult(task_id, app=celery_app)
    response = {"task_id": task_id, "state": task.state}
    if task.state == "PENDING":
        response["message"] = "Task is queued"
    elif task.state == "PROGRESS":
        response["progress"] = task.info
    elif task.state == "SUCCESS":
        response["result"] = task.result
    elif task.state == "FAILURE":
        response["error"] = str(task.info)
    return response

@router.get("/{task_id}/stream")
async def stream_docking_status(task_id: str, request: Request):
    """SSE endpoint برای مشاهده پیشرفت داکینگ به صورت زنده"""
    async def event_generator():
        last_state = None
        while True:
            if await request.is_disconnected():
                break
                
            task = AsyncResult(task_id, app=celery_app)
            payload = {"task_id": task_id, "state": task.state}
            if task.state == "PROGRESS":
                payload["progress"] = task.info
            elif task.state == "SUCCESS":
                payload["result"] = task.result
            elif task.state == "FAILURE":
                payload["error"] = str(task.info)
            
            current_state = f"{task.state}-{json.dumps(task.info) if task.info else ''}"
            if current_state != last_state:
                yield f"data: {json.dumps(payload, ensure_ascii=False)}\n\n"
                last_state = current_state
            
            if task.state in ("SUCCESS", "FAILURE"):
                break
            await asyncio.sleep(2)

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )