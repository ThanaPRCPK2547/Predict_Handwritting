# ThaiDigit AI — Local Server Setup Guide

## Prerequisites

- Python 3.9+
- pip

---

## Step-by-Step

### 1. Open terminal in project root

```bash
cd /mnt/c/Users/kapun/OneDrive/Desktop/Predict_Handwritting
```

### 2. Create a virtual environment

```bash
python -m venv venv
```

### 3. Activate the virtual environment

**Linux / WSL:**
```bash
source venv/bin/activate
```

**Windows (Command Prompt):**
```cmd
venv\Scripts\activate
```

**Windows (PowerShell):**
```powershell
venv\Scripts\Activate.ps1
```

You should see `(venv)` appear in your terminal prompt.

### 4. Install dependencies

```bash
pip install -r backend/requirements.txt
```

### 5. Verify environment variables

The `.env` file should already exist with:

```
SECRET_KEY= read .env.example
DATABASE_URL= read .env.example
MODEL_PATH= read .env.example
```

If missing or corrupted, copy from `.env.example` and generate a new `SECRET_KEY`:

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

### 6. Start the FastAPI server

```bash
uvicorn backend.app.main:app --reload --port 8000
```

### 7. Verify the server is running

Open in your browser:

- **API**: [http://localhost:8000](http://localhost:8000)
- **Swagger Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)

### 8. Open the frontend

Open `frontend/index.html` in your browser (double-click the file or serve it separately).

The frontend connects to `http://localhost:8000` by default.

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| `uvicorn: command not found` | Activate your venv first, then `pip install uvicorn` |
| Port 8000 already in use | Change port: `uvicorn backend.app.main:app --reload --port 8001` |
| Model not found | Verify `ml/models/thai_number_model.keras` exists |
| Database errors | Delete `thai_digit.db` and restart — SQLAlchemy will recreate it |
