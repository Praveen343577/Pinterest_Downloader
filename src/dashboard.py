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
    sessions = math.ceil(total_links / config.SESSION_SIZE)
    console.print(f"\nTotal Links: {total_links} | Total Sessions: {sessions}\n"
                  f"Log File: {log_name}\nSaved to: {config.OUTPUT_BASE}\n")

def print_preflight_success(msg):
    console.print(f"{msg}\n")

def print_summary(total_time, success, failed, exists, empty):
    console.print(f"\nExecution complete in {total_time:.2f}s\nSuccess: {success} | Failed: {failed} | exists: {exists} | empty: {empty}\n")

class DashboardManager:
    def __init__(self, total_links):
        self.total_links = total_links
        self.current_index = 0
        self.success_count = 0
        self.fail_count = 0
        self.exists_count = 0
        self.empty_count = 0
        self.current_url = ""
        self.link_items = 0
        self.link_start_time = 0
        self.session_pos = 1
        self.link_pos = 1
        self.total_start_time = time.time()
        self.durations = []
        self.delay_msg = ""
        self.pass_num = 1
        
        self.progress = Progress(
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TextColumn("{task.completed} / {task.total} links")
        )
        self.task_id = self.progress.add_task("Overall Progress", total=self.total_links, success=0, fail=0, exists=0, empty=0)
        self.live = Live(self.progress, console=console, refresh_per_second=4)
        self.results_log = []

    def _build_grid(self):
        grid = Table.grid(expand=True)
        grid.add_column()
        
        grid.add_row(self.progress)
        
        stats_line = Text.from_markup(f"[green][SUCCESS : {self.success_count}][/green] [red][FAILED : {self.fail_count}][/red] [blue][EXISTS : {self.exists_count}][/blue] [dark_orange][EMPTY : {self.empty_count}][/dark_orange]")
        grid.add_row(stats_line)
        grid.add_row("")
        
        trunc_url = self.current_url[:80] + ("..." if len(self.current_url) > 80 else "")
        pass_str = f" (Pass {self.pass_num}/{config.MAX_RETRIES})" if hasattr(self, 'pass_num') and self.pass_num > 1 else ""
        grid.add_row(Text(f"Downloading{pass_str}: {trunc_url}", style="yellow"))
        
        grid.add_row("")
        
        elapsed = time.time() - self.link_start_time if self.link_start_time else 0
        ips = (self.link_items / elapsed) if elapsed > 0 else 0
        stats_str = f"DL: {self.link_items} items | {int(elapsed//60):02d}:{int(elapsed%60):02d} | {ips:.1f} items/sec | Session {self.session_pos} - Link {self.link_pos} / {config.SESSION_SIZE}"
        grid.add_row(Text(stats_str, style="magenta"))
        
        total_elapsed = time.time() - self.total_start_time
        if self.durations:
            avg_time = sum(self.durations) / len(self.durations)
            eta = avg_time * (self.total_links - self.current_index - 1)
            eta_str = f"{int(eta//60):02d}:{int(eta%60):02d}"
        else:
            eta_str = "--:--"
            
        overall_str = f"Total Time Elapsed: {int(total_elapsed//3600):02d}:{int((total_elapsed%3600)//60):02d}:{int(total_elapsed%60):02d} | ETA: {eta_str}"
        text_row = Text(overall_str, style="yellow")
        
        if self.delay_msg:
            style = "magenta" if "cooldown" in self.delay_msg.lower() else "yellow"
            text_row.append(f" | {self.delay_msg}", style=style)
            
        grid.add_row(text_row)
        
        if self.results_log:
            grid.add_row("")
            for res in self.results_log:
                grid.add_row(res)
                
        return grid

    def update_display(self):
        self.live.update(self._build_grid())

    def __enter__(self):
        self.live.start()
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.live.stop()

    def new_link(self, index, url, pass_num=1):
        self.current_index = index
        self.current_url = url
        self.link_items = 0
        self.link_start_time = time.time()
        self.session_pos = (index // config.SESSION_SIZE) + 1
        self.link_pos = (index % config.SESSION_SIZE) + 1
        self.delay_msg = ""
        self.pass_num = pass_num
        self.update_display()

    def update_item_count(self, count):
        self.link_items = count
        self.update_display()

    def complete_link(self, status, duration, is_retry=False):
        if is_retry:
            if status == "SUCCESS":
                self.success_count += 1
                self.fail_count -= 1
            elif status == "EXISTS":
                self.exists_count += 1
                self.fail_count -= 1
            elif status == "EMPTY":
                self.empty_count += 1
                self.fail_count -= 1
        else:
            if status == "SUCCESS":
                self.success_count += 1
            elif status == "EXISTS":
                self.exists_count += 1
            elif status == "EMPTY":
                self.empty_count += 1
            else:
                self.fail_count += 1
        self.durations.append(duration)
        
        if is_retry:
            self.progress.update(self.task_id, success=self.success_count, fail=self.fail_count, exists=self.exists_count, empty=self.empty_count)
        else:
            self.progress.update(self.task_id, advance=1, success=self.success_count, fail=self.fail_count, exists=self.exists_count, empty=self.empty_count)
            
        self.update_display()

    def set_delay(self, remaining):
        self.delay_msg = f"Next link in {remaining:.1f}s..."
        self.update_display()

    def set_cooldown(self, remaining, total):
        self.delay_msg = f"Session cooldown - resuming in {int(remaining//60):02d}:{int(remaining%60):02d} of {int(total//60):02d}:{int(total%60):02d}"
        self.update_display()

    def print_result(self, status, items, url):
        trunc_url = url[:80] + ("..." if len(url) > 80 else "")
        if status == "SUCCESS":
            status_text = f"[green]{status:<10}[/green]"
        elif status == "EXISTS":
            status_text = f"[blue]{status:<10}[/blue]"
        elif status == "EMPTY":
            status_text = f"[dark_orange]{status:<10}[/dark_orange]"
        else:
            status_text = f"[red]{status:<10}[/red]"
        self.results_log.append(f"{status_text} [{items}] {trunc_url}")
        self.update_display()

    def add_line_space(self):
        self.results_log.append("")
        self.update_display()
