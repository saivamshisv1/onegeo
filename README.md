# OneGeo Well-Log Web System

Complete web system for LAS ingestion, storage, visualization, AI-assisted interpretation, and a bonus chat endpoint.

## Architecture
- **Backend**: FastAPI + SQLAlchemy + SQLite.
- **Storage strategy**:
  - Original LAS files saved in `data/uploads/`.
  - Optional S3 upload when `S3_BUCKET` and AWS credentials are configured.
  - Parsed depth-indexed rows stored in relational tables (`well_log_files`, `well_log_points`).
- **Frontend**: Plain HTML/CSS/JavaScript + Plotly for interactive depth plots (zoom/pan).

## Features mapped to problem statement
1. **Architecture**: clear frontend/backend split over REST APIs.
2. **File ingestion & storage**: `.las` upload, parser for `~Curve` + `~A`, persisted raw and parsed data, optional S3.
3. **Visualization**: pick curves + depth range, interactive curve plotting against depth.
4. **AI-assisted interpretation**: rule-based heuristic interpreter with statistics and recommendations.
5. **Chatbot (bonus)**: lightweight Q&A endpoint backed by selected interval analysis.

## Run locally
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Open http://localhost:8000

## Optional S3 configuration
Set these environment variables before starting server:
- `S3_BUCKET`
- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`
- `AWS_REGION`

## API quick reference
- `POST /api/uploads` (multipart file)
- `GET /api/files`
- `GET /api/files/{file_id}/curves?curves=GR&curves=RHOB&start_depth=...&end_depth=...`
- `POST /api/files/{file_id}/interpret`
- `POST /api/files/{file_id}/chat`
