"""Build the hw_networking tab. Thin wrapper: all logic lives in pipeline.build_universe_payload."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_all

if __name__ == "__main__":
    raise SystemExit(build_all.main(["--only", "hw_networking"]))
