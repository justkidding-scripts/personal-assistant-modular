#!/usr/bin/env python3
import typer
from assistant import Assistant

app = typer.Typer()
assistant = Assistant()

@app.command()
def ask(query: str):
    """Ask the personal assistant a question."""
    result = assistant.handle(query)
    typer.echo(result["answer"]) 

@app.command()
def shell():
    """Interactive shell for continuous commands."""
    typer.echo("Type 'exit' or 'quit' to leave.")
    while True:
        try:
            line = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if line.lower() in {"exit", "quit"}:
            break
        if not line:
            continue
        res = assistant.handle(line)
        typer.echo(res.get("answer", ""))

@app.command()
def watch(cmd: str = typer.Argument(..., help="Command to run repeatedly"), every: int = typer.Option(60, help="Seconds between runs")):
    """Run a command repeatedly at an interval."""
    import time
    typer.echo(f"Watching: {cmd} (every {every}s)")
    while True:
        res = assistant.handle(cmd)
        typer.echo(res.get("answer", ""))
        time.sleep(every)

rag_app = typer.Typer(help="RAG commands")

@rag_app.command("add")
def rag_add(path: str):
    res = assistant.handle(f"rag add {path}")
    typer.echo(res.get("answer", ""))

@rag_app.command("ask")
def rag_ask(question: str):
    res = assistant.handle(f"rag ask {question}")
    typer.echo(res.get("answer", ""))

@rag_app.command("status")
def rag_status():
    res = assistant.handle("rag status")
    typer.echo(res.get("answer", ""))

app.add_typer(rag_app, name="rag")

if __name__ == "__main__":
    app()
