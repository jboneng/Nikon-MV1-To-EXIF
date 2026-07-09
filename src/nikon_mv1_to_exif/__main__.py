"""Entry point for the Nikon MV-1 to EXIF application."""

from __future__ import annotations

import sys

from nikon_mv1_to_exif.runtime_bootstrap import prepare_frozen_runtime, run_smoke_test


def main() -> None:
    prepare_frozen_runtime()

    if len(sys.argv) > 1 and sys.argv[1] == "--smoke-test":
        raise SystemExit(run_smoke_test())

    from nikon_mv1_to_exif.app import run_app

    raise SystemExit(run_app())


if __name__ == "__main__":
    main()
