import click
import os
from rich.console import Console
from rich.panel import Panel
from rich.theme import Theme
from .inference import run_llm, CUSTOM_THEME
from .utils import download_model_if_needed

console = Console(theme=CUSTOM_THEME)

@click.group()
def cli():
    """🎒 [bold accent]Pixel[/bold accent]: Your Adorable Offline Study Companion 🎓"""
    pass

@cli.command()
def run():
    """Start a lesson with your cute AI tutor"""
    with console.status("[bold accent]Pixel is grabbing his backpack...", spinner="bouncingBar"):
        download_model_if_needed()
    run_llm()

@cli.command()
def install():
    """Download local weights and set up the environment"""
    with console.status("[bold accent]Downloading Pixel-AI model weights...", spinner="earth"):
        download_model_if_needed()
    console.print(Panel(
        "[bold accent]Success![/bold accent] Model installed and ready for local inference.",
        title="[bold accent]Installation Complete[/bold accent]",
        border_style="accent",
        title_align="left"
    ))

if __name__ == "__main__":
    cli()
