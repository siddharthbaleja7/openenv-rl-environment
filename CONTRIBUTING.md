## Contributing

Run tests:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install -e .
pip install pytest
pytest -q
```

To run the API locally:

```bash
uvicorn server.app:app --host 0.0.0.0 --port 7860
```

Please open PRs against `main`. Add tests for new behavior and keep changes small and focused.
