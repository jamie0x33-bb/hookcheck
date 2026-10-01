# hookcheck

Lightweight CLI for verifying webhook endpoint configurations. Confirms reachability, validates response schemas, and measures latency.

## Install

```bash
pip install -e .
```

## Usage

```bash
hookcheck verify https://your-app.example.com/webhook
hookcheck verify https://your-app.example.com/webhook --method GET --timeout 5
```

## Features

- Endpoint reachability checks with configurable timeout
- HTTP status and latency reporting
- TLS verification
- JSON response schema validation
- Exit codes for CI integration (`0` = pass, `1` = fail)

## Development

```bash
python -m pytest tests/ -v
```

## License

MIT
