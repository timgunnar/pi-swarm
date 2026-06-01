import typer
from rich.console import Console
from pi_cli.client import APIClient

app = typer.Typer(help="推理服务", no_args_is_help=True)
console = Console()


@app.command("chat")
def chat(
    prompt: str = typer.Option(..., "--prompt", "-p", help="输入提示词"),
    model: str = typer.Option("qwen2.5:7b", "--model", "-m", help="模型名"),
    temperature: float = typer.Option(0.7, "--temp", "-t"),
):
    client = APIClient()
    try:
        result = client.chat(model, prompt, temperature)
        msg = result.get("message", {})
        console.print(f"\n[bold cyan]🤖 {result['model']}[/bold cyan]")
        console.print(msg.get("content", ""))
        console.print(f"\n[dim]tokens: {result.get('eval_count', 0)} | duration: {result.get('total_duration', 0) / 1e9:.2f}s[/dim]")
    except Exception as e:
        console.print(f"[red]推理失败: {e}[/red]")
