import typer
from rich.console import Console
from rich.table import Table
from pi_cli.client import APIClient

app = typer.Typer(help="节点管理", no_args_is_help=True)
console = Console()


@app.command("list")
def list_nodes():
    client = APIClient()
    nodes = client.list_nodes()
    table = Table(title="Pi 推理节点")
    table.add_column("名称"); table.add_column("状态"); table.add_column("角色")
    for n in nodes:
        role = n.get("labels", {}).get("pi-role", "-")
        icon = {"online": "🟢", "offline": "🔴"}.get(n["status"], "🟡")
        table.add_row(n["name"], f"{icon} {n['status']}", role)
    console.print(table)


@app.command("add")
def add_node(host: str, name: str = typer.Option(None, "--name", "-n")):
    client = APIClient()
    result = client.join_node(host, name)
    console.print(f"[green]{result['message']}[/green]")
    if result.get("join_command"):
        console.print(f"\n运行命令:\n  [bold]{result['join_command']}[/bold]")


@app.command("drain")
def drain_node(name: str):
    client = APIClient()
    client.drain_node(name)
    console.print(f"[yellow]节点 {name} 已下线[/yellow]")
