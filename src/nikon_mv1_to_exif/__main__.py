"""Entry point for the Nikon MV-1 to EXIF application."""

from nikon_mv1_to_exif.app import run_app


def main() -> None:
    raise SystemExit(run_app())


if __name__ == "__main__":
    main()
