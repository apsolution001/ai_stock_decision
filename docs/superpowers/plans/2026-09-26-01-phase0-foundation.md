# Phase 0: Foundation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** A runnable, tested, containerized backend skeleton with CI. Every later phase plugs into it.

**Architecture:** The `backend/` Python package `app` is managed with `uv`. It holds a FastAPI app factory, pydantic-settings config, and a torch-free device detector (the Laya install comes in phase 3). Docker Compose runs the API, Postgres 16 and Redis 7. GitHub Actions runs ruff, mypy and pytest.

**Tech Stack:** Python 3.11, uv, FastAPI, pydantic-settings, pytest, httpx, ruff, mypy, Docker Compose, GitHub Actions.

## Global Constraints

- Python `>=3.11`; dependency management via `uv` (`backend/pyproject.toml`, committed `uv.lock`).
- Market: Indian equities (NSE / BSE). Timezone for schedules: `Asia/Kolkata`.
- Laya device auto-detect order: `cuda` → `mps` → `cpu`.
- Settings are read from env vars prefixed `ASD_` (e.g. `ASD_DATABASE_URL`).
- Every API response surface that shows decisions must carry the disclaimer: "Decision-support tool only. Not investment advice."
- Tests must never download the Laya checkpoint (use `FakeEngine` from phase 3 onward).

---

### Task 1: Backend package with `/health` endpoint

**Files:**
- Create: `backend/pyproject.toml`
- Create: `backend/app/__init__.py`
- Create: `backend/app/main.py`
- Create: `backend/app/api/__init__.py`
- Create: `backend/app/api/health.py`
- Test: `backend/tests/test_health.py`

**Interfaces:**
- Produces: `app.main.create_app() -> FastAPI`; module-level `app.main.app`; `GET /health -> {"status": "ok", "version": str, "device": str}` (`device` is wired in Task 2).

- [ ] **Step 1: Create `backend/pyproject.toml`**

```toml
[project]
name = "ai-stock-decision"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = [
    "fastapi>=0.115",
    "uvicorn[standard]>=0.30",
    "pydantic-settings>=2.4",
]

[dependency-groups]
dev = [
    "pytest>=8.3",
    "httpx>=0.27",
    "ruff>=0.6",
    "mypy>=1.11",
]

[tool.pytest.ini_options]
testpaths = ["tests"]

[tool.ruff]
line-length = 100
target-version = "py311"

[tool.ruff.lint]
select = ["E", "F", "I", "B", "UP", "SIM"]

[tool.mypy]
python_version = "3.11"
strict = true
packages = ["app"]

[[tool.mypy.overrides]]
module = ["torch", "torch.*"]
ignore_missing_imports = true
```

- [ ] **Step 2: Write the failing test** `backend/tests/test_health.py`

```python
from fastapi.testclient import TestClient

from app.main import create_app


def test_health_returns_ok() -> None:
    client = TestClient(create_app())
    response = client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["version"] == "0.1.0"
```

- [ ] **Step 3: Run it and confirm it fails**

Run: `cd backend && uv sync && uv run pytest tests/test_health.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'app.main'`

- [ ] **Step 4: Implement**

`backend/app/__init__.py`:
```python
__version__ = "0.1.0"
```

`backend/app/api/__init__.py`: empty file.

`backend/app/api/health.py`:
```python
from fastapi import APIRouter

from app import __version__

router = APIRouter()


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "version": __version__, "device": "unknown"}
```

`backend/app/main.py`:
```python
from fastapi import FastAPI

from app import __version__
from app.api.health import router as health_router


def create_app() -> FastAPI:
    application = FastAPI(title="AI Stock Decision", version=__version__)
    application.include_router(health_router)
    return application


app = create_app()
```

- [ ] **Step 5: Run the tests and confirm they pass**

Run: `cd backend && uv run pytest -v`
Expected: `1 passed`

- [ ] **Step 6: Commit**

```bash
git add backend/pyproject.toml backend/uv.lock backend/app backend/tests
git commit -m "feat(backend): scaffold FastAPI app with /health"
```

---

### Task 2: Settings and device detection

**Files:**
- Create: `backend/app/core/__init__.py`
- Create: `backend/app/core/config.py`
- Create: `backend/app/core/device.py`
- Modify: `backend/app/api/health.py`
- Create: `.env.example`
- Test: `backend/tests/test_config.py`, `backend/tests/test_device.py`

**Interfaces:**
- Produces: `app.core.config.Settings` with fields `database_url: str`, `redis_url: str`, `laya_model_id: str = "convaiinnovations/laya"`, `laya_device: str = "auto"`, `decision_threshold: float = 0.7`, `timezone: str = "Asia/Kolkata"`; `app.core.config.get_settings() -> Settings` (cached).
- Produces: `app.core.device.resolve_device(preference: str) -> str`, which returns one of `"cuda" | "mps" | "cpu"`.

- [ ] **Step 1: Write the failing tests**

`backend/tests/test_config.py`:
```python
import pytest

from app.core.config import Settings


def test_defaults() -> None:
    s = Settings()
    assert s.laya_model_id == "convaiinnovations/laya"
    assert s.laya_device == "auto"
    assert s.decision_threshold == 0.7
    assert s.timezone == "Asia/Kolkata"


def test_env_override(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ASD_DECISION_THRESHOLD", "0.85")
    assert Settings().decision_threshold == 0.85
```

`backend/tests/test_device.py`:
```python
import sys
import types

import pytest

from app.core.device import resolve_device


def _fake_torch(cuda: bool, mps: bool) -> types.ModuleType:
    torch = types.ModuleType("torch")
    torch.cuda = types.SimpleNamespace(is_available=lambda: cuda)  # type: ignore[attr-defined]
    torch.backends = types.SimpleNamespace(  # type: ignore[attr-defined]
        mps=types.SimpleNamespace(is_available=lambda: mps)
    )
    return torch


def test_explicit_preference_is_respected() -> None:
    assert resolve_device("cpu") == "cpu"


def test_auto_prefers_cuda(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setitem(sys.modules, "torch", _fake_torch(cuda=True, mps=True))
    assert resolve_device("auto") == "cuda"


def test_auto_falls_back_to_mps(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setitem(sys.modules, "torch", _fake_torch(cuda=False, mps=True))
    assert resolve_device("auto") == "mps"


def test_auto_without_torch_is_cpu(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setitem(sys.modules, "torch", None)
    assert resolve_device("auto") == "cpu"
```

- [ ] **Step 2: Run them and confirm they fail**

Run: `cd backend && uv run pytest tests/test_config.py tests/test_device.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'app.core'`

- [ ] **Step 3: Implement**

`backend/app/core/__init__.py`: empty file.

`backend/app/core/config.py`:
```python
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="ASD_", env_file=".env", extra="ignore")

    database_url: str = "postgresql+psycopg://asd:asd@localhost:5432/asd"
    redis_url: str = "redis://localhost:6379/0"
    laya_model_id: str = "convaiinnovations/laya"
    laya_device: str = "auto"
    decision_threshold: float = 0.7
    timezone: str = "Asia/Kolkata"


@lru_cache
def get_settings() -> Settings:
    return Settings()
```

`backend/app/core/device.py`:
```python
def resolve_device(preference: str) -> str:
    """Return the torch device to run Laya on: cuda -> mps -> cpu when 'auto'."""
    if preference != "auto":
        return preference
    try:
        import torch
    except ImportError:
        return "cpu"
    if torch.cuda.is_available():
        return "cuda"
    if torch.backends.mps.is_available():
        return "mps"
    return "cpu"
```

(Setting `sys.modules["torch"] = None` makes `import torch` raise `ImportError`, which is how the no-torch test works.)

Replace `backend/app/api/health.py` with:
```python
from fastapi import APIRouter

from app import __version__
from app.core.config import get_settings
from app.core.device import resolve_device

router = APIRouter()


@router.get("/health")
def health() -> dict[str, str]:
    device = resolve_device(get_settings().laya_device)
    return {"status": "ok", "version": __version__, "device": device}
```

`.env.example` (repo root):
```dotenv
ASD_DATABASE_URL=postgresql+psycopg://asd:asd@postgres:5432/asd
ASD_REDIS_URL=redis://redis:6379/0
ASD_LAYA_MODEL_ID=convaiinnovations/laya
ASD_LAYA_DEVICE=auto
ASD_DECISION_THRESHOLD=0.7
```

- [ ] **Step 4: Run all the tests and confirm they pass**

Run: `cd backend && uv run pytest -v`
Expected: `7 passed`

- [ ] **Step 5: Commit**

```bash
git add backend/app/core backend/app/api/health.py backend/tests .env.example
git commit -m "feat(backend): add settings and Laya device auto-detection"
```

---

### Task 3: Docker Compose stack

**Files:**
- Create: `backend/Dockerfile`
- Create: `backend/.dockerignore`
- Create: `docker-compose.yml`

**Interfaces:**
- Produces: services `api` (port 8000), `postgres` (5432, db/user/pass `asd`), `redis` (6379); named volumes `pgdata` and `hf_cache` (mounted at `/root/.cache/huggingface` for the Laya checkpoint later).

- [ ] **Step 1: Write `backend/Dockerfile`**

```dockerfile
FROM python:3.11-slim
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv
WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev
COPY app ./app
ENV PATH="/app/.venv/bin:$PATH"
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

`backend/.dockerignore`:
```
.venv
__pycache__
.pytest_cache
.mypy_cache
.ruff_cache
tests
```

- [ ] **Step 2: Write `docker-compose.yml`**

```yaml
services:
  api:
    build: ./backend
    ports: ["8000:8000"]
    env_file: [.env]
    depends_on:
      postgres: { condition: service_healthy }
      redis: { condition: service_started }
    volumes:
      - hf_cache:/root/.cache/huggingface

  postgres:
    image: postgres:16
    environment:
      POSTGRES_DB: asd
      POSTGRES_USER: asd
      POSTGRES_PASSWORD: asd
    ports: ["5432:5432"]
    volumes: [pgdata:/var/lib/postgresql/data]
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U asd"]
      interval: 5s
      retries: 10

  redis:
    image: redis:7
    ports: ["6379:6379"]

volumes:
  pgdata:
  hf_cache:
```

- [ ] **Step 3: Verify the stack runs**

Run: `cp .env.example .env && docker compose up -d --build && curl -s localhost:8000/health`
Expected: `{"status":"ok","version":"0.1.0","device":"cpu"}`
Then: `docker compose down`

- [ ] **Step 4: Commit**

```bash
git add backend/Dockerfile backend/.dockerignore docker-compose.yml
git commit -m "build: add Docker Compose stack (api, postgres, redis)"
```

---

### Task 4: Lint, type-check and CI

**Files:**
- Create: `.pre-commit-config.yaml`
- Create: `.github/workflows/ci.yml`

**Interfaces:**
- Produces: a CI job `backend` that must pass on every push and pull request to `main`.

- [ ] **Step 1: Run the checks locally and fix anything they report**

Run: `cd backend && uv run ruff check . && uv run ruff format --check . && uv run mypy`
Expected: `All checks passed!`, `… files already formatted`, `Success: no issues found`
(If formatting fails, run `uv run ruff format .` and re-run.)

- [ ] **Step 2: Write `.pre-commit-config.yaml`**

```yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.6.9
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.6.0
    hooks:
      - id: end-of-file-fixer
      - id: trailing-whitespace
      - id: check-yaml
```

- [ ] **Step 3: Write `.github/workflows/ci.yml`**

```yaml
name: CI
on:
  push:
    branches: [main]
  pull_request:

jobs:
  backend:
    runs-on: ubuntu-latest
    defaults:
      run:
        working-directory: backend
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v3
      - run: uv python install 3.11
      - run: uv sync --frozen
      - run: uv run ruff check .
      - run: uv run ruff format --check .
      - run: uv run mypy
      - run: uv run pytest -v
```

- [ ] **Step 4: Commit and push, then confirm CI is green**

```bash
git add .pre-commit-config.yaml .github/workflows/ci.yml
git commit -m "ci: add ruff, mypy and pytest workflow"
git push
```
Expected: the GitHub Actions "CI" run for this commit passes.

---

## Done criteria for Phase 0
- `uv run pytest` passes (7 tests); ruff and mypy are clean.
- `docker compose up` serves `/health` with the resolved device.
- CI is green on `main`.
