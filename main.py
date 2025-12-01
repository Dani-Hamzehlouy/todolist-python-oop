from src.cli.cli_app import CLIApp, print_cli_deprecation_warning


def main() -> None:
    """Launches the Phase 2 CLI application."""
    # Deprecated CLI entry point; prefer the FastAPI Web API going forward.
    print_cli_deprecation_warning()
    app = CLIApp()
    app.run()


if __name__ == "__main__":
    main()
