import argparse
import json
from .generate import generate
from .clean import clean
from .db import load
from .analyze import analyze


def main():
    parser = argparse.ArgumentParser(description="Reproducible fictional iGaming analytics pipeline")
    parser.add_argument("command", choices=["generate", "clean", "load", "analyze", "all"])
    args = parser.parse_args()
    actions = {"generate": generate, "clean": clean, "load": load, "analyze": analyze}
    for name in actions if args.command == "all" else [args.command]:
        print(json.dumps({name: actions[name]()}, indent=2, default=str))


if __name__ == "__main__":
    main()
