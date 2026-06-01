import typer
from rich.console import Console
from rich.table import Table
from pi_cli.client import APIClient

app = typer.Typer(help="模型管理", no_args_is_help=True)
console = Console()


@app.command("list")
def list_models():
    client = APIClient()
    models = client.list_models()
    table = Table(title="已部署模型")
    table.add_column("模型名"); table.add_column("节点数"); table.add_column("节点")
    for m in models:
        table.add_row(m["name"], str(len(m.get("nodes", []))), ", ".join(m.get("nodes", [])))
    console.print(table)


@app.command("deploy")
def deploy_model(name: str):
    client = APIClient()
    result = client.deploy_model(name)
    console.print(f"[green]✓ 模型 {name} 部署到: {', '.join(result['nodes'])}[/green]")
