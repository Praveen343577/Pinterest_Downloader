import time
import math
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, BarColumn, TextColumn
from rich.text import Text
from rich.live import Live
from rich.table import Table
import config

console = Console()

def print_header(total_links, log_name):
    sessions = math.ceil(total_links / 25)
    console.print(Panel(
        f"Valid Links: {total_links} | Total Sessions: {sessions}\n"
        f"Log File: {log_name}\nOutput Dir: {config.OUTPUT_BASE}",
        title="Pinterest Downloader", style="cyan"
    ))

def print_preflight_success(msg):
    console.print(Panel(msg, title="Preflight Checks Passed", style="green"))

def print_summary(total_time, success, failed):
    console.print(Panel(f"Execution complete in {total_time:.2f}s\nSuccess: {success} | Failed: {failed}", title="Summary", style="bold blue"))

class DashboardManager:
    def __init__(self, total_links):
        self.total_links = total_links
        self.current_index = 0
        self.success_count = 0
        self.fail_count = 0
        self.current_url = ""
        self.link_items = 0
        self.link_start_time = 0
        self.session_pos = 1
        self.link_pos = 1
        self.total_start_time = time.time()
        self.durations = []
        self.delay_msg = ""
        
        self.progress = Progress(
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TextColumn("{task.completed} / {task.total} links"),
            TextColumn("[green]✔ {task.fields[success]}[/green] [red]✖ {task.fields[fail]}[/red]")
        )
        self.task_id = self.progress.add_task("Overall Progress", total=self.total_links, success=0, fail=0)
        self.live = Live(self.progress, console=console, refresh_per_second=4)

    def _build_grid(self):
        grid = Table.grid(expand=True)
        grid.add_column()
        
        grid.add_row(self.progress)
        
        trunc_url = self.current_url[:80] + ("..." if len(self.current_url) > 80 else "")
        grid.add_row(Text(f"URL: {trunc_url}", style="dim white"))
        
        elapsed = time.time() - self.link_start_time if self.link_start_time else 0
        ips = (self.link_items / elapsed) if elapsed > 0 else 0
        stats_str = f"↓ {self.link_items} items | {int(elapsed//60):02d}:{int(elapsed%60):02d} | {ips:.1f} items/sec | Session {self.session_pos} — Link {self.link_pos} / 25"
        grid.add_row(Text(stats_str, style="cyan"))
        
        total_elapsed = time.time() - self.total_start_time
        if self.durations:
            avg_time = sum(self.durations) / len(self.durations)
            eta = avg_time * (self.total_links - self.current_index - 1)
            eta_str = f"{int(eta//60):02d}:{int(eta%60):02d}"
        else:
            eta_str = "--:--"
            
        overall_str = f"Total Elapsed: {int(total_elapsed//3600):02d}:{int((total_elapsed%3600)//60):02d}:{int(total_elapsed%60):02d} | ETA: {eta_str}"
        grid.add_row(Text(overall_str, style="yellow"))
        
        if self.delay_msg:
            style = "magenta" if "cooldown" in self.delay_msg.lower() else "yellow"
            grid.add_row(Text(self.delay_msg, style=style))
            
        return grid

    def update_display(self):
        self.live.update(self._build_grid())

    def __enter__(self):
        self.live.start()
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.live.stop()

    def new_link(self, index, url):
        self.current_index = index
        self.current_url = url
        self.link_items = 0
        self.link_start_time = time.time()
        self.session_pos = (index // 25) + 1
        self.link_pos = (index % 25) + 1
        self.delay_msg = ""
        self.update_display()

    def update_item_count(self, count):
        self.link_items = count
        self.update_display()

    def complete_link(self, success, duration):
        if success:
            self.success_count += 1
        else:
            self.fail_count += 1
        self.durations.append(duration)
        self.progress.update(self.task_id, advance=1, success=self.success_count, fail=self.fail_count)
        self.update_display()

    def set_delay(self, remaining):
        self.delay_msg = f"Next link in {remaining:.1f}s..."
        self.update_display()

    def set_cooldown(self, remaining, total):
        self.delay_msg = f"Session cooldown — resuming in {int(remaining//60):02d}:{int(remaining%60):02d} of {int(total//60):02d}:{int(total%60):02d}"
        self.update_display()

    def print_result(self, success, status, items, url):
        mark = "[green]✔[/green]" if success else "[red]✖[/red]"
        trunc_url = url[:80] + ("..." if len(url) > 80 else "")
        console.log(f"{mark} {status:<10} [{items}] {trunc_url}")