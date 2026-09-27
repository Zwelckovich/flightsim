"""Dispatch a bounded Opus task and retain a local, inspectable exchange record."""
import json
import pathlib
import subprocess
import sys
import uuid
import argparse

sys.stdout.reconfigure(encoding="utf-8")
project = pathlib.Path(__file__).resolve().parents[2]
base = pathlib.Path(__file__).resolve().parent / ".runs"
base.mkdir(exist_ok=True)
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("prompt", type=pathlib.Path)
parser.add_argument("run_name")
parser.add_argument("--review", action="store_true")
parser.add_argument("--effort", choices=["low", "medium", "high", "max"], default="max")
options = parser.parse_args()
prompt_path = options.prompt
run_name = options.run_name
review = options.review
session = str(uuid.uuid4())
available = "Read,Glob,Grep,WebFetch,WebSearch" if review else "Read,Edit,Write,Glob,Grep,WebFetch,WebSearch"
args = [str(pathlib.Path.home() / ".local/bin/claude.exe"), "-p", "--model", "claude-opus-5-5",
        "--effort", options.effort, "--safe-mode", "--permission-mode", "dontAsk", "--tools", available,
        "--allowedTools", available, "--session-id", session, "--output-format", "stream-json", "--verbose"]
(base / (run_name + ".meta.json")).write_text(json.dumps({"model": "claude-opus-5-5", "effort": options.effort,
    "session": session, "prompt": str(prompt_path), "review": review}, indent=2), encoding="utf-8")
with (base / (run_name + ".stderr.log")).open("w", encoding="utf-8") as err, (base / (run_name + ".events.jsonl")).open("w", encoding="utf-8") as log:
    proc = subprocess.Popen(args, cwd=str(project), stdin=subprocess.PIPE,
        stdout=subprocess.PIPE, stderr=err, text=True, encoding="utf-8", creationflags=subprocess.CREATE_NO_WINDOW)
    proc.stdin.write(prompt_path.read_text(encoding="utf-8")); proc.stdin.close()
    result = None
    for line in proc.stdout:
        log.write(line); log.flush()
        try: event = json.loads(line)
        except json.JSONDecodeError: continue
        if event.get("type") == "system" and event.get("subtype") == "init":
            print("Opus initialized:", event.get("model"), flush=True)
            if event.get("model") != "claude-opus-5-5":
                proc.terminate(); raise SystemExit("Unexpected model; stopped without fallback")
        if event.get("type") == "assistant":
            for block in event.get("message", {}).get("content", []):
                if block.get("type") == "tool_use":
                    print("Opus:", block.get("name"), flush=True)
        if event.get("type") == "result": result = event
    code = proc.wait()
if result:
    (base / (run_name + ".result.json")).write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    (base / (run_name + ".result.md")).write_text(result.get("result", ""), encoding="utf-8")
    print(json.dumps({k: result.get(k) for k in ["subtype", "is_error", "result", "modelUsage", "permission_denials"]}, ensure_ascii=False), flush=True)
else: print("No result; see local stderr log", flush=True)
raise SystemExit(code or (1 if not result or result.get("is_error") else 0))
