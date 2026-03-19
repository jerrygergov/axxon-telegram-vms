import os, sys, json, time, datetime as dt
from pathlib import Path
sys.path.insert(0, str(Path('scripts').resolve()))
from axxon_web_api import AxxonClient

# Setup via environment
host = os.environ.get('AXXON_HOST') or '127.0.0.1'
user = os.environ.get('AXXON_USER') or 'root'
password = os.environ.get('AXXON_PASS') or ''
port = int(os.environ.get('AXXON_PORT') or '80')
scheme = os.environ.get('AXXON_SCHEME') or 'http'
c = AxxonClient(host, user, password, port=port, scheme=scheme)

results = {}
def test(name, fn):
    print(f"Testing {name}...", file=sys.stderr)
    try:
        results[name] = fn()
        print(f"PASS: {name}", file=sys.stderr)
    except Exception as e:
        results[name] = f"FAIL: {str(e)}"
        print(f"FAIL: {name}", file=sys.stderr)

test("server_usage", lambda: c.server_usage(domain=True))
test("list_cameras", lambda: c.list_cameras(view='VIEW_MODE_FULL'))
# Use read_events instead of events
test("events", lambda: c.read_events(
    begin=(dt.datetime.now(dt.timezone.utc) - dt.timedelta(seconds=3600)).strftime("%Y%m%dT%H%M%S"),
    end=dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%S"),
    limit=10
))

out_dir = Path('tmp')
out_dir.mkdir(exist_ok=True)
with open(out_dir / 'smoke_test_results.json', 'w') as f:
    json.dump(results, f, indent=2)
