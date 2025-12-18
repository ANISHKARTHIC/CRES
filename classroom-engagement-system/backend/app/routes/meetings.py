from fastapi import APIRouter, UploadFile, File, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse
import os
import uuid
import logging
from pathlib import Path
from app.config import settings
from app.models.meeting import SourceType, MeetingAnalysis
from pymongo import MongoClient
from bson.objectid import ObjectId

logger = logging.getLogger("uvicorn.error")


router = APIRouter()

# Initialize MongoDB connection
mongodb_client = MongoClient(settings.mongodb_url)
db = mongodb_client[settings.db_name]
meetings_collection = db["meetings"]

# Store active WebSocket connections
active_websockets = {}


@router.post("/analyze-meeting")
async def analyze_meeting(file: UploadFile = File(...), meeting_id: str = None, source_type: str = "teams"):
    """
    Async endpoint to upload and analyze a meeting recording
    Hands off to Celery worker for diarization
    """
    
    try:
        if not meeting_id:
            meeting_id = str(uuid.uuid4())

        # Prepare upload directory (absolute path) and ensure it exists
        upload_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../uploads"))
        Path(upload_dir).mkdir(parents=True, exist_ok=True)

        # Log incoming upload metadata for debugging
        logger.info("Incoming upload: filename=%s content_type=%s meeting_id=%s", file.filename, file.content_type, meeting_id)

        # Validate file is audio (accept common variants)
        valid_audio_types = {
            "audio/wav",
            "audio/x-wav",
            "audio/wave",
            "audio/vnd.wave",
            "audio/mpeg",
            "audio/mp3",
            "audio/x-mpeg",
            "audio/x-matroska",
        }

        if (file.content_type is None) or (file.content_type not in valid_audio_types):
            logger.warning("Rejected upload due to content_type=%s", file.content_type)
            raise HTTPException(
                status_code=400,
                detail=f"Invalid file type. Accepted types: {sorted(valid_audio_types)}. Received: {file.content_type}"
            )

        # Save uploaded file safely
        file_extension = os.path.splitext(file.filename)[1] or ".wav"
        file_path = os.path.join(upload_dir, f"{meeting_id}{file_extension}")

        try:
            content = await file.read()
            with open(file_path, "wb") as f:
                f.write(content)
        except Exception as write_err:
            logger.exception("Failed to write upload to %s", file_path)
            raise HTTPException(status_code=500, detail=f"Failed to save uploaded file: {str(write_err)}")

        # Hand off to Celery worker (import locally to avoid circular import)
        from app.tasks.diarization import analyze_audio_task

        task = analyze_audio_task.delay(
            file_path=file_path,
            meeting_id=meeting_id,
            source_type=source_type,
            audio_file_name=file.filename
        )

        return JSONResponse({
            "status": "processing",
            "meeting_id": meeting_id,
            "task_id": task.id,
            "message": "Audio analysis started. Check status with task_id"
        })

    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Unhandled error in analyze_meeting endpoint")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/analysis/{meeting_id}")
async def get_analysis(meeting_id: str):
    """
    Retrieve meeting analysis from MongoDB
    """
    try:
        # Try to find by meeting_id first
        analysis = meetings_collection.find_one({"meeting_id": meeting_id})
        
        if not analysis:
            raise HTTPException(status_code=404, detail="Analysis not found")
        
        # Convert ObjectId to string
        analysis["_id"] = str(analysis["_id"])
        
        return JSONResponse({
            "status": "success",
            "data": analysis
        })
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/task-status/{task_id}")
async def get_task_status(task_id: str):
    """
    Check Celery task status
    """
    from app.tasks.celery_app import celery_app
    
    task = celery_app.AsyncResult(task_id)
    
    return JSONResponse({
        "task_id": task_id,
        "status": task.status,
        "result": task.result if task.status == "SUCCESS" else None
    })


@router.websocket("/ws/live-class/{meeting_id}")
async def websocket_live_class(websocket: WebSocket, meeting_id: str):
    """
    WebSocket endpoint for live class audio streaming
    Accepts audio chunks from frontend
    """
    await websocket.accept()
    active_websockets[meeting_id] = websocket
    
    try:
        # Initialize meeting session
        session_data = {
            "meeting_id": meeting_id,
            "source_type": "live",
            "chunks": [],
            "duration": 0
        }
        
        while True:
            # Receive audio chunk
            data = await websocket.receive_bytes()
            
            session_data["chunks"].append(data)
            
            # Send acknowledgment
            await websocket.send_json({
                "status": "chunk_received",
                "meeting_id": meeting_id,
                "chunk_count": len(session_data["chunks"])
            })
    
    except WebSocketDisconnect:
        del active_websockets[meeting_id]
        print(f"Client {meeting_id} disconnected")
    except Exception as e:
        print(f"WebSocket error: {str(e)}")
        del active_websockets[meeting_id]


@router.post("/finalize-live-session/{meeting_id}")
async def finalize_live_session(meeting_id: str):
    """
    Finalize a live class session and trigger analysis
    """
    try:
        # Process the accumulated chunks
        # This would combine chunks and trigger analysis
        
        return JSONResponse({
            "status": "success",
            "message": f"Live session {meeting_id} finalized",
            "meeting_id": meeting_id
        })
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/all-analyses")
async def get_all_analyses(limit: int = 50):
    """
    Get all meeting analyses (paginated)
    """
    try:
        analyses = list(meetings_collection.find().sort("created_at", -1).limit(limit))
        
        # Convert ObjectIds to strings
        for analysis in analyses:
            analysis["_id"] = str(analysis["_id"])
        
        return JSONResponse({
            "status": "success",
            "count": len(analyses),
            "data": analyses
        })
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
