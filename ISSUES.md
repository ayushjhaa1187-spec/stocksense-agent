# Repository Issues

## Discrepancies between DOCS.md and actual file structure

The following files and directories mentioned in DOCS.md are missing from the repository:

- `src/data_processor.py`
- `src/discount_optimizer.py`
- `src/scheduler.py`
- `app/dashboard.py`
- `app/templates/`
- `app/static/`
- `tests/test_agent.py`
- `tests/test_expiry_logic.py`
- `tests/test_discount_calc.py`
- `docs/ARCHITECTURE.md`
- `docs/API_DOCS.md`
- `docs/DEPLOYMENT.md`

## Code Issues

- `src/agent.py` fails to run because dependencies (`pandas`) are missing in the environment.
- `src/agent.py` does not check for file existence before loading CSV.
- The project structure is incomplete for a production-ready application.
