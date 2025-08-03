"""CLI application."""

from pathlib import Path
from typing import Annotated

import typer
from feedly.api_client.session import FeedlySession, FileAuthStore
from logzero import logger

from feedly_saved_entries_processor.feedly_client import FeedlyClient

app = typer.Typer()


@app.command()
def main(
    token_dir: Annotated[
        Path | None,
        typer.Option(exists=True, file_okay=False),
    ] = None,
) -> None:
    """Process saved entries."""
    if token_dir is None:
        token_dir = Path.home() / ".config" / "feedly"
    auth = FileAuthStore(token_dir=token_dir)
    feedly_session = FeedlySession(auth=auth)
    client = FeedlyClient(feedly_session=feedly_session)
    entries = list(client.fetch_saved_entries())
    logger.info(f"Number of saved entries: {len(entries)}")


if __name__ == "__main__":
    app()
