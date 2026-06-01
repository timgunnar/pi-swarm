import typer
from rich.console import Console
from rich.table import Table
from pi_cli.commands import nodes, models, inference
from pi_cli.client import APIClient

app = typer.Typer(name="k3s-pi", help="pi-swarm 集群管理命令行工具", no_args_is_help=True)

app.add_typer(nodes.app, name="node", help="节点管理")
app.add_typer(models.app, name="model", help="模型管理")
app.add_typer(inference.app, name="infer", help="推理操作")


@app.command()
def status():
    """集群状态总览."""
    client = APIClient()
    console = Console()
    try:
        nodes_list = client.list_nodes()
    except Exception as e:
        console.print(f"[red]无法连接后端: {e}[/red]")
        return

    online = sum(1 for n in nodes_list if n["status"] == "online")
    console.print(f"\n[bold]🖥 pi-swarm[/bold]")
    console.print(f"节点: {len(nodes_list)} 总数 / {online} 在线\n")

    table = Table(title="节点列表")
    table.add_column("名称")
    table.add_column("状态")
    table.add_column("版本")
    for n in nodes_list:
        icon = {"online": "🟢", "offline": "🔴"}.get(n["status"], "🟡")
        table.add_row(n["name"], f"{icon} {n['status']}", n.get("kubelet_version", ""))
    console.print(table)


if __name__ == "__main__":
    app()
