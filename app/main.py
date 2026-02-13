from pathlib import Path

from fastapi import Depends, FastAPI, File, HTTPException, Query, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session

from .database import Base, engine, get_db
from .interpretation import interpret_data
from .las_parser import parse_las_text
from .models import WellLogFile, WellLogPoint
from .schemas import ChatRequest, CurveSeriesResponse, FileSummary, InterpretRequest
from .storage import save_original_file

app = FastAPI(title="OneGeo Mudlogging Mass Spectrometer")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)

app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
def home() -> FileResponse:
    return FileResponse(Path("static/index.html"))


@app.post("/api/uploads", response_model=FileSummary)
async def upload_las(file: UploadFile = File(...), db: Session = Depends(get_db)):
    if not file.filename.lower().endswith(".las"):
        raise HTTPException(status_code=400, detail="Only .las files are supported.")

    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    storage = save_original_file(file.filename, content)

    try:
        parsed = parse_las_text(content.decode("utf-8", errors="ignore"))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    record = WellLogFile(
        filename=file.filename,
        original_path=storage["local_path"],
        s3_key=storage.get("s3_key"),
        min_depth=min(parsed.depth),
        max_depth=max(parsed.depth),
        curves=parsed.curves,
    )
    db.add(record)
    db.flush()

    for depth, row in zip(parsed.depth, parsed.rows):
        db.add(WellLogPoint(file_id=record.id, depth=depth, values=row))

    db.commit()
    db.refresh(record)
    return record


@app.get("/api/files", response_model=list[FileSummary])
def list_files(db: Session = Depends(get_db)):
    return db.query(WellLogFile).order_by(WellLogFile.uploaded_at.desc()).all()


@app.get("/api/files/{file_id}/curves", response_model=CurveSeriesResponse)
def fetch_curve_series(
    file_id: int,
    curves: list[str] = Query(default=[]),
    start_depth: float | None = None,
    end_depth: float | None = None,
    db: Session = Depends(get_db),
):
    file_record = db.get(WellLogFile, file_id)
    if not file_record:
        raise HTTPException(status_code=404, detail="File not found")

    selected_curves = curves or file_record.curves[1:]
    query = db.query(WellLogPoint).filter(WellLogPoint.file_id == file_id)
    if start_depth is not None:
        query = query.filter(WellLogPoint.depth >= start_depth)
    if end_depth is not None:
        query = query.filter(WellLogPoint.depth <= end_depth)

    rows = query.order_by(WellLogPoint.depth.asc()).all()
    if not rows:
        raise HTTPException(status_code=404, detail="No data in selected depth range")

    depth = [row.depth for row in rows]
    curve_map = {name: [row.values.get(name) for row in rows] for name in selected_curves}
    return CurveSeriesResponse(depth=depth, curves=curve_map)


@app.post("/api/files/{file_id}/interpret")
def interpret(
    file_id: int,
    payload: InterpretRequest,
    db: Session = Depends(get_db),
):
    data = fetch_curve_series(
        file_id,
        curves=payload.curves,
        start_depth=payload.start_depth,
        end_depth=payload.end_depth,
        db=db,
    )
    return interpret_data(data.depth, data.curves)


@app.post("/api/files/{file_id}/chat")
def chat_assistant(file_id: int, payload: ChatRequest, db: Session = Depends(get_db)):
    analysis = interpret(
        file_id,
        InterpretRequest(
            curves=payload.curves,
            start_depth=payload.start_depth,
            end_depth=payload.end_depth,
        ),
        db,
    )
    message = payload.message.lower()
    insight = "\n".join(f"- {item}" for item in analysis["insights"])

    if "summary" in message or "overview" in message:
        response = f"Interval summary:\n{insight}"
    elif "shale" in message:
        response = "Shale indication is mainly inferred from GR values. " + insight
    else:
        response = "I analyzed the selected interval with rule-based petrophysical heuristics:\n" + insight

    return {"answer": response, "analysis": analysis}
