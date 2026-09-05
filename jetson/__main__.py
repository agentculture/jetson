"""Entry point for ``python -m jetson``."""

from __future__ import annotations

import sys

from jetson.cli import main

if __name__ == "__main__":
    sys.exit(main())
