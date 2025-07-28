from rich import print


def print_error(msg: str) -> None:
    print(f"[red bold]ERROR:[/red bold] [red]{msg}[/red]")


def print_info(msg: str) -> None:
    print(f"[blue]{msg}[/blue]")
