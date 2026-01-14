import time
from datetime import datetime, timedelta
import random
from models import MarketEvent
from engine import IntelligenceEngine
from analyst import Analyst

from rich.console import Console
from rich.layout import Layout
from rich.panel import Panel
from rich.live import Live
from rich.table import Table
from rich.text import Text
from rich.align import Align
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn
from rich import box
from rich.style import Style

console = Console()

class FinanceTerminalUI:
    def __init__(self):
        self.engine = IntelligenceEngine(decay_rate=0.2)
        self.analyst = Analyst()
        self.current_time = datetime(2024, 1, 1, 9, 0, 0)
        self.event_idx = 0
        self.recent_events = []
        self.state_history = []
        
        # Scenario events
        self.scenario_events = [
            (datetime(2024, 1, 1, 9, 30), "Market Open - Normal trading", 2.0, "📈"),
            (datetime(2024, 1, 1, 10, 15), "Breaking: Inflation data higher than expected", 7.5, "🔥"),
            (datetime(2024, 1, 1, 10, 45), "Rumor: Central Bank emergency meeting", 6.0, "⚠️"),
            (datetime(2024, 1, 1, 11, 0), "Tech Sector sell-off begins", 5.0, "📉"),
            (datetime(2024, 1, 1, 11, 30), "Major Exchange halts trading due to glitch", 8.0, "🚨"),
            (datetime(2024, 1, 1, 14, 0), "Central Bank reassures markets - nothing wrong", 3.0, "✅"),
        ]
        
    def get_state_color(self, state):
        """Return color gradient based on market state"""
        colors = {
            "STABLE": "bright_green",
            "HIGH_VOLATILITY": "yellow",
            "CRASH": "bright_red",
            "BULL_RUN": "bright_cyan",
            "BEAR_MARKET": "bright_magenta",
            "UNKNOWN": "bright_black"
        }
        return colors.get(state, "white")
    
    def get_state_emoji(self, state):
        """Return emoji for market state"""
        emojis = {
            "STABLE": "😌",
            "HIGH_VOLATILITY": "😰",
            "CRASH": "🚨",
            "BULL_RUN": "🚀",
            "BEAR_MARKET": "🐻",
            "UNKNOWN": "❓"
        }
        return emojis.get(state, "")
    
    def create_header(self):
        """Create stunning header with gradient effect"""
        title = Text()
        title.append("╔═══════════════════════════════════════════════════════════════╗\n", style="bold cyan")
        title.append("║  ", style="bold cyan")
        title.append("FINANCE-X", style="bold magenta on black")
        title.append(" ", style="")
        title.append("INTELLIGENCE TERMINAL", style="bold bright_white")
        title.append("                    ║\n", style="bold cyan")
        title.append("║  ", style="bold cyan")
        title.append("Real-time Market Analysis & Crisis Detection System", style="italic bright_cyan")
        title.append("     ║\n", style="bold cyan")
        title.append("╚═══════════════════════════════════════════════════════════════╝", style="bold cyan")
        
        return Panel(
            Align.center(title),
            style="on #0a0a0a",
            border_style="bright_cyan",
            box=box.DOUBLE
        )
    
    def create_time_panel(self):
        """Create time display panel"""
        time_text = Text()
        time_text.append("🕐 ", style="bold yellow")
        time_text.append(self.current_time.strftime('%Y-%m-%d %H:%M:%S'), style="bold bright_white")
        
        return Panel(
            Align.center(time_text),
            title="[bold bright_cyan]CURRENT TIME[/]",
            border_style="cyan",
            style="on #1a1a2e"
        )
    
    def create_state_panel(self, snapshot):
        """Create market state panel with visual indicators"""
        state = snapshot.state.value if hasattr(snapshot.state, 'value') else str(snapshot.state)
        weight = snapshot.risk_score
        
        state_color = self.get_state_color(state)
        state_emoji = self.get_state_emoji(state)
        
        # Create visual weight bar
        bar_length = 30
        filled = int((weight / 10.0) * bar_length)
        bar = "█" * filled + "░" * (bar_length - filled)
        
        content = Text()
        content.append(f"{state_emoji} STATE: ", style="bold white")
        content.append(f"{state}\n", style=f"bold {state_color}")
        content.append(f"⚡ WEIGHT: ", style="bold white")
        content.append(f"{weight:.2f}\n", style=f"bold {state_color}")
        content.append(f"[{bar}] ", style=state_color)
        content.append(f"{int((weight/10.0)*100)}%", style=f"bold {state_color}")
        
        return Panel(
            Align.center(content),
            title="[bold bright_yellow]MARKET STATE[/]",
            border_style=state_color,
            style="on #1a1a2e"
        )
    
    def create_events_table(self):
        """Create recent events table"""
        table = Table(
            show_header=True,
            header_style="bold bright_cyan on #0f3460",
            border_style="cyan",
            box=box.ROUNDED,
            expand=True
        )
        
        table.add_column("🕐 Time", style="bright_white", width=12)
        table.add_column("📰 Event", style="bright_yellow", width=40)
        table.add_column("💥 Impact", justify="right", style="bright_red", width=8)
        
        # Show last 5 events
        for event in self.recent_events[-5:]:
            time_str = event['time'].strftime('%H:%M')
            desc = event['desc'][:38] + "..." if len(event['desc']) > 38 else event['desc']
            impact = f"{event['impact']:.1f}"
            
            # Color code impact
            if event['impact'] >= 7:
                impact_style = "bold bright_red"
            elif event['impact'] >= 5:
                impact_style = "bold yellow"
            else:
                impact_style = "bold green"
            
            table.add_row(
                f"{event['emoji']} {time_str}",
                desc,
                Text(impact, style=impact_style)
            )
        
        return Panel(
            table,
            title="[bold bright_magenta]RECENT MARKET EVENTS[/]",
            border_style="magenta",
            style="on #16213e"
        )
    
    def create_analyst_panel(self, report):
        """Create analyst insight panel"""
        # Parse report to add styling
        styled_text = Text()
        
        lines = report.split('\n')
        for line in lines:
            if 'STABLE' in line:
                styled_text.append(line + '\n', style="green")
            elif 'HIGH_VOLATILITY' in line or 'VOLATILITY' in line:
                styled_text.append(line + '\n', style="yellow")
            elif 'CRASH' in line:
                styled_text.append(line + '\n', style="bold bright_red")
            elif line.startswith('💡'):
                styled_text.append(line + '\n', style="bold bright_cyan")
            elif line.startswith('📊'):
                styled_text.append(line + '\n', style="bright_white")
            else:
                styled_text.append(line + '\n', style="white")
        
        return Panel(
            styled_text,
            title="[bold bright_green]🤖 AI ANALYST INSIGHTS[/]",
            border_style="green",
            style="on #0f3460",
            box=box.ROUNDED
        )
    
    def create_metrics_panel(self, snapshot):
        """Create metrics panel with key statistics"""
        table = Table(
            show_header=False,
            border_style="yellow",
            box=box.SIMPLE,
            expand=True
        )
        
        table.add_column("Metric", style="bold bright_white")
        table.add_column("Value", style="bold bright_yellow", justify="right")
        
        table.add_row("📊 Total Events", str(len(self.recent_events)))
        table.add_row("⚡ Current Weight", f"{snapshot.risk_score:.2f}")
        table.add_row("🎯 State Changes", str(len(self.state_history)))
        table.add_row("🔥 Max Impact", f"{max([e['impact'] for e in self.recent_events], default=0):.1f}")
        
        return Panel(
            table,
            title="[bold bright_yellow]SYSTEM METRICS[/]",
            border_style="yellow",
            style="on #1a1a2e"
        )
    
    def create_layout(self, snapshot, report):
        """Create the main layout"""
        layout = Layout()
        
        # Split into sections
        layout.split_column(
            Layout(name="header", size=7),
            Layout(name="main", ratio=1),
            Layout(name="footer", size=3)
        )
        
        # Main section split
        layout["main"].split_row(
            Layout(name="left", ratio=2),
            Layout(name="right", ratio=1)
        )
        
        # Left section split
        layout["left"].split_column(
            Layout(name="events", ratio=1),
            Layout(name="analyst", ratio=1)
        )
        
        # Right section split
        layout["right"].split_column(
            Layout(name="time", size=5),
            Layout(name="state", size=8),
            Layout(name="metrics", ratio=1)
        )
        
        # Populate sections
        layout["header"].update(self.create_header())
        layout["time"].update(self.create_time_panel())
        layout["state"].update(self.create_state_panel(snapshot))
        layout["events"].update(self.create_events_table())
        layout["analyst"].update(self.create_analyst_panel(report))
        layout["metrics"].update(self.create_metrics_panel(snapshot))
        
        # Footer
        footer_text = Text()
        footer_text.append("⚡ LIVE ", style="bold bright_green blink")
        footer_text.append("| Powered by Finance-X Intelligence Engine | ", style="bright_black")
        footer_text.append("Press Ctrl+C to exit", style="italic bright_black")
        
        layout["footer"].update(Panel(
            Align.center(footer_text),
            style="on #0a0a0a",
            border_style="bright_black"
        ))
        
        return layout
    
    def run_simulation(self):
        """Run the simulation with live UI updates"""
        console.clear()
        
        # Show loading animation
        with console.status("[bold bright_cyan]Initializing Financial Intelligence System...", spinner="dots") as status:
            time.sleep(2)
        
        # Initial snapshot
        snapshot = self.engine.detect_state(self.current_time)
        report = "System initialized. Awaiting market data..."
        
        try:
            with Live(self.create_layout(snapshot, report), console=console, refresh_per_second=4, screen=True) as live:
                for _ in range(20):  # Run for 20 iterations
                    # Ingest events
                    while self.event_idx < len(self.scenario_events) and self.scenario_events[self.event_idx][0] <= self.current_time:
                        t, desc, impact, emoji = self.scenario_events[self.event_idx]
                        evt = MarketEvent(
                            timestamp=t,
                            event_type="NEWS",
                            description=desc,
                            base_impact=impact,
                            asset_class="GENERAL"
                        )
                        self.engine.ingest(evt)
                        self.recent_events.append({
                            'time': t,
                            'desc': desc,
                            'impact': impact,
                            'emoji': emoji
                        })
                        self.event_idx += 1
                    
                    # Update engine
                    self.engine.apply_decay(self.current_time)
                    snapshot = self.engine.detect_state(self.current_time)
                    
                    # Track state changes
                    current_state_value = snapshot.state.value if hasattr(snapshot.state, 'value') else str(snapshot.state)
                    if not self.state_history or self.state_history[-1] != current_state_value:
                        self.state_history.append(current_state_value)
                    
                    # Get analyst report
                    report = self.analyst.explain_situation(snapshot)
                    
                    # Update display
                    live.update(self.create_layout(snapshot, report))
                    
                    # Advance time
                    self.current_time += timedelta(minutes=30)
                    time.sleep(1.5)  # Pause for readability
                    
        except KeyboardInterrupt:
            console.print("\n[bold bright_red]Simulation terminated by user.[/]")
        
        # Show completion message
        console.print("\n[bold bright_green]✅ Simulation Complete![/]")
        console.print(f"[bright_cyan]Total Events Processed: {len(self.recent_events)}[/]")
        console.print(f"[bright_cyan]State Changes: {len(self.state_history)}[/]")


if __name__ == "__main__":
    ui = FinanceTerminalUI()
    ui.run_simulation()
