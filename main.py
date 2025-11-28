from src.cli.cli_app import CLIApp


def main() -> None:
    """Launches the Phase 2 CLI application."""
    app = CLIApp()
    app.run()


if __name__ == "__main__":
    main()
