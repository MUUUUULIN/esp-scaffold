"""CLI entry point for esp-scaffold."""
import click
from esp_scaffold.generator import ProjectGenerator, VALID_CHIPS, VALID_PERIPHERALS


@click.group()
def main():
    """esp-scaffold: ESP-IDF project scaffolding tool.

    Generate ready-to-compile ESP-IDF projects from the command line.
    """
    pass


@main.command()
@click.option(
    "--chip", default="esp32s3",
    type=click.Choice(VALID_CHIPS),
    help="Target ESP32 chip (default: esp32s3)"
)
@click.option(
    "--peripherals", default="",
    help="Comma-separated list of peripherals: spi,i2c,uart,pwm,gpio"
)
@click.option(
    "--freertos-tasks", default=1,
    type=click.IntRange(0, 10),
    help="Number of FreeRTOS task skeletons to generate (default: 1)"
)
@click.option(
    "--output", "-o", default=".",
    type=click.Path(),
    help="Output directory (default: current directory)"
)
@click.option(
    "--name", "-n", default="esp-project",
    help="Project name (default: esp-project)"
)
def create(chip, peripherals, freertos_tasks, output, name):
    """Create a new ESP-IDF project scaffold.

    Example:

        esp-scaffold create --chip esp32s3 --peripherals spi,i2c --freertos-tasks 3 -o my_project
    """
    peri_list = [p.strip() for p in peripherals.split(",") if p.strip()]

    # Validate peripherals
    invalid = [p for p in peri_list if p not in VALID_PERIPHERALS]
    if invalid:
        click.echo(f"Error: Invalid peripheral(s): {', '.join(invalid)}")
        click.echo(f"Valid options: {', '.join(VALID_PERIPHERALS)}")
        return

    generator = ProjectGenerator(chip=chip)
    generator.generate(
        project_name=name,
        output_dir=output,
        peripherals=peri_list,
        num_tasks=freertos_tasks,
    )

    click.echo(f"\n✅ Project '{name}' created at: {output}")
    click.echo(f"   Chip: {chip}")
    click.echo(f"   Peripherals: {', '.join(peri_list) if peri_list else 'none'}")
    click.echo(f"   FreeRTOS tasks: {freertos_tasks}")
    click.echo(f"\n   cd {output}")
    click.echo(f"   idf.py set-target {chip}")
    click.echo(f"   idf.py build")


@main.command()
def list():
    """List supported chips and peripherals."""
    click.echo("Supported chips:")
    for chip in VALID_CHIPS:
        click.echo(f"  - {chip}")
    click.echo("\nSupported peripherals:")
    for p in VALID_PERIPHERALS:
        click.echo(f"  - {p}")
