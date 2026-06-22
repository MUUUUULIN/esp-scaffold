"""Project generator using Jinja2 templates."""
import os
from jinja2 import Environment, FileSystemLoader

VALID_CHIPS = ["esp32s3"]
VALID_PERIPHERALS = ["spi", "i2c", "uart", "pwm", "gpio"]

# Peripheral → ESP-IDF component dependencies (for docs only in MVP)
PERIPHERAL_INFO = {
    "spi":    {"bus": "SPI2_HOST", "dma": True,  "pins": {"mosi": -1, "miso": -1, "sclk": -1, "cs": -1}},
    "i2c":    {"bus": "I2C_NUM_0", "pins": {"sda": -1, "scl": -1}},
    "uart":   {"bus": "UART_NUM_1", "pins": {"tx": -1, "rx": -1}},
    "pwm":    {"timer": "LEDC_TIMER_0", "mode": "LEDC_LOW_SPEED_MODE", "pins": []},
    "gpio":   {"pins": []},
}

# Human-readable task names
TASK_NAMES = [
    "sensor_task",
    "communication_task",
    "control_task",
    "display_task",
    "storage_task",
    "network_task",
    "monitor_task",
    "actuator_task",
    "logger_task",
    "alarm_task",
]


class ProjectGenerator:
    """Generate an ESP-IDF project from templates."""

    def __init__(self, chip="esp32s3"):
        if chip not in VALID_CHIPS:
            raise ValueError(f"Unsupported chip: {chip}. Valid: {VALID_CHIPS}")
        self.chip = chip

        template_dir = os.path.join(os.path.dirname(__file__), "templates", chip)
        if not os.path.isdir(template_dir):
            raise FileNotFoundError(f"Template directory not found: {template_dir}")
        self.env = Environment(loader=FileSystemLoader(template_dir))
        self.env.trim_blocks = True
        self.env.lstrip_blocks = True

    def generate(self, project_name, output_dir, peripherals, num_tasks):
        """Generate the full project scaffold."""
        output_path = os.path.join(output_dir, project_name)
        os.makedirs(output_path, exist_ok=True)

        # Gather context for templates
        ctx = self._build_context(project_name, peripherals, num_tasks)

        # 1. Top-level files
        self._render("CMakeLists.txt.j2",
                     os.path.join(output_path, "CMakeLists.txt"), ctx)
        self._render("sdkconfig.defaults.j2",
                     os.path.join(output_path, "sdkconfig.defaults"), ctx)
        self._render("partitions.csv.j2",
                     os.path.join(output_path, "partitions.csv"), ctx)

        # 2. main/ directory
        main_dir = os.path.join(output_path, "main")
        os.makedirs(main_dir, exist_ok=True)
        self._render("main/CMakeLists.txt.j2",
                     os.path.join(main_dir, "CMakeLists.txt"), ctx)
        self._render("main/main.c.j2",
                     os.path.join(main_dir, "main.c"), ctx)
        self._render("main/gpio_config.c.j2",
                     os.path.join(main_dir, "gpio_config.c"), ctx)
        self._render("main/gpio_config.h.j2",
                     os.path.join(main_dir, "gpio_config.h"), ctx)

        # 3. Peripheral components
        if peripherals:
            comp_dir = os.path.join(output_path, "components")
            os.makedirs(comp_dir, exist_ok=True)
            for peri in peripherals:
                peri_dir = os.path.join(comp_dir, f"driver_{peri}")
                os.makedirs(peri_dir, exist_ok=True)
                self._render(f"components/{peri}/CMakeLists.txt.j2",
                             os.path.join(peri_dir, "CMakeLists.txt"), ctx)
                self._render(f"components/{peri}/component.h.j2",
                             os.path.join(peri_dir, f"{peri}_driver.h"), ctx)
                self._render(f"components/{peri}/component.c.j2",
                             os.path.join(peri_dir, f"{peri}_driver.c"), ctx)

    def _build_context(self, project_name, peripherals, num_tasks):
        """Build the template context dictionary."""
        tasks = []
        for i in range(num_tasks):
            tasks.append({
                "name": TASK_NAMES[i % len(TASK_NAMES)],
                "priority": 5 - i if i < 5 else 1,
                "stack_size": 4096,
                "delay_ms": 1000 * (i + 1),
            })

        peri_ctx = []
        for p in peripherals:
            info = PERIPHERAL_INFO.get(p, {})
            peri_ctx.append({
                "name": p,
                "bus": info.get("bus", ""),
                "pins": info.get("pins", {}),
                "timer": info.get("timer", ""),
                "mode": info.get("mode", ""),
                "dma": info.get("dma", False),
            })

        return {
            "project_name": project_name,
            "chip": self.chip,
            "peripherals": peri_ctx,
            "tasks": tasks,
            "num_tasks": num_tasks,
            "has_wifi": any(p["name"] in ("spi",) for p in peri_ctx),  # simplified heuristic
        }

    def _render(self, template_name, output_path, context):
        """Render a single template and write it."""
        template = self.env.get_template(template_name)
        content = template.render(**context)
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(content)
