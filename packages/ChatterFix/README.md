# ChatterFix AI Operations Hub

## Features
- Modular multi-agent dashboard (FredFix, BulletTrain, LineSmart, ...)
- File upload, chat, work order, feedback, export
- Firestore/local logging, notifications, RBAC

## Setup
1. Clone repo
2. Install requirements: `pip install -r requirements.txt`
3. Set environment variables (see `.env.example`)
4. Run Streamlit: `streamlit run pages/8_FredFix_Agent.py`

## Deployment
- Backend: Cloud Run (see /FredFix/core)
- Frontend: Streamlit Cloud, GCP, AWS, or VM

## Extending
- Add new agent pages and update `sidebar.py`
- See `tests/` for test scaffolding

## License
MIT
