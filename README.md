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

## Deploy frontend to GitHub Pages
GitHub Pages can host the **frontend only**. The FastAPI backend must run on another host (Render, Railway, EC2, etc.).

1. Ensure your default branch is `main` (or update `.github/workflows/deploy-pages.yml`).
2. Push this repository to GitHub.
3. In GitHub repository settings, enable **Pages** and set source to **GitHub Actions**.
4. Set backend URL in `static/config.js`:
   ```js
   window.ONEGEO_API_BASE = 'https://your-backend-domain.com';
   ```
5. Push to `main`; workflow `.github/workflows/deploy-pages.yml` will publish `static/`.

### Backend hosting note
The backend already enables CORS for all origins in `app/main.py`, so a GitHub Pages frontend can call the API directly.

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
