"""Allow running as a module: python -m vv."""

from vv.cli import main

if __name__ == "__main__":
    raise SystemExit(main())
