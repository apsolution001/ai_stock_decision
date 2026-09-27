# Git Workflow

- `main` is always runnable. Work happens on feature branches: `feat/<topic>`, `fix/<topic>`, `docs/<topic>`.
- Conventional commits: `feat:`, `fix:`, `docs:`, `test:`, `refactor:`, `chore:`.
- Small commits, one logical change each; tests are in the same commit as the code.
- **Never commit** `.env`, tokens, downloaded market data (`data/`), or model checkpoints.
- Changes touching `risk/`, `broker/` or order flow get reviewed by the `risk-safety-auditor` agent before merge.
- Before merge: `uv run pytest`, `ruff`, `mypy` all pass.
