"""
Enhanced Finance-X Terminal with Indian Stock Market Integration
Main interactive terminal combining crisis detection + Indian market analysis
"""

import time
from datetime import datetime, timedelta
import random
from models import MarketEvent
from engine import IntelligenceEngine
from analyst import Analyst
from india_engine import IndiaMarketEngine

from rich.console import Console
from rich.layout import Layout
from rich.panel import Panel
from rich.live import Live
from rich.table import Table
from rich.text import Text
from rich.align import Align
from rich.prompt import Prompt
from rich import box
from rich.columns import Columns

console = Console()

class EnhancedFinanceTerminal:
    def __init__(self):
        # Crisis detection system
        self.engine = IntelligenceEngine(decay_rate=0.2)
        self.analyst = Analyst()
        
        # Indian stock market engine
        self.india_engine = IndiaMarketEngine(default_categories=['NIFTY_50', 'BANK', 'IT'])
        
        self.mode = "menu"  # menu, crisis, india_market
        self.current_india_view = "nifty50"  # nifty50, sectors, search, summary
        
    def show_main_menu(self):
        """Display main menu"""
        console.clear()
        
        title = Text()
        title.append("╔════════════════════════════════════════════════════════════════╗\n", style="bold cyan")
        title.append("║  ", style="bold cyan")
        title.append("FINANCE-X", style="bold magenta on black")
        title.append(" ", style="")
        title.append("INTELLIGENCE TERMINAL", style="bold bright_white")
        title.append("                     ║\n", style="bold cyan")
        title.append("║  ", style="bold cyan")
        title.append("Global Markets + Indian Stock Analysis", style="italic bright_cyan")
        title.append("              ║\n", style="bold cyan")
        title.append("╚════════════════════════════════════════════════════════════════╝", style="bold cyan")
        
        console.print(Panel(Align.center(title), style="on #0a0a0a", border_style="bright_cyan", box=box.DOUBLE))
        
        menu = Table(show_header=False, box=box.ROUNDED, border_style="cyan", expand=True)
        menu.add_column("Option", style="bold bright_white", width=10)
        menu.add_column("Description", style="bright_cyan")
        
        menu.add_row("1", "🚨  Crisis Detection System (Live Simulation)")
        menu.add_row("2", "📈  Indian Stock Market (240+ Stocks)")
        menu.add_row("3", "🏦  Banking Sector Analysis")
        menu.add_row("4", "💻  IT Sector Analysis")
        menu.add_row("5", "🔍  Search Indian Stocks")
        menu.add_row("6", "📊  Market Summary & Sentiment")
        menu.add_row("7", "📚  Coverage Statistics")
        menu.add_row("Q", "❌  Exit")
        
        console.print(Panel(menu, title="[bold bright_yellow]MAIN MENU[/]", border_style="yellow"))
        
        choice = Prompt.ask(
            "\n[bold bright_cyan]Select Option[/]",
            choices=["1", "2", "3", "4", "5", "6", "7", "q", "Q"],
            default="2"
        )
        
        return choice.upper()
    
    def show_indian_stocks_live(self, category='NIFTY_50', sector=None):
        """Display Indian stocks with live data"""
        console.clear()
        
        with console.status(f"[bold bright_cyan]Fetching {category} stocks...", spinner="dots"):
            if sector:
                data = self.india_engine.get_sector_stocks(sector)
                title_text = f"{sector.upper()} Sector Stocks"
            else:
                data = self.india_engine.fetch_market_snapshot(categories=[category])
                title_text = f"{category.replace('_', ' ')} Stocks"
        
        # Create header
        header = Panel(
            Align.center(Text(title_text, style="bold bright_cyan")),
            style="on #0a0a0a",
            border_style="cyan"
        )
        console.print(header)
        
        # Create stocks table
        table = Table(
            show_header=True,
            header_style="bold bright_cyan on #0f3460",
            border_style="cyan",
            box=box.ROUNDED,
            expand=True
        )
        
        table.add_column("Symbol", style="bold bright_white", width=15)
        table.add_column("Price (Rs.)", justify="right", style="bright_yellow", width=12)
        table.add_column("Change", justify="right", width=10)
        table.add_column("Change %", justify="right", width=10)
        table.add_column("Sector", style="bright_cyan", width=20)
        
        for stock in data[:20]:  # Show top 20
            # Color code based on performance
            if stock['change_pct'] > 0:
                change_style = "bold bright_green"
                arrow = "▲"
            elif stock['change_pct'] < 0:
                change_style = "bold bright_red"
                arrow = "▼"
            else:
                change_style = "bright_white"
                arrow = "●"
            
            table.add_row(
                stock['symbol'],
                f"{stock['price']:.2f}",
                Text(f"{arrow} {stock['change']:.2f}", style=change_style),
                Text(f"{stock['change_pct']:+.2f}%", style=change_style),
                stock.get('sector', 'N/A')
            )
        
        console.print(table)
        console.print(f"\n[bright_black]Showing {len(data[:20])} of {len(data)} stocks[/]")
        console.print("\n[bold bright_cyan]Press Enter to return to menu...[/]")
        input()
    
    def show_market_summary(self):
        """Display market summary with sentiment analysis"""
        console.clear()
        
        with console.status("[bold bright_cyan]Analyzing market sentiment...", spinner="dots"):
            summary = self.india_engine.get_category_summary(['NIFTY_50', 'BANK', 'IT', 'PHARMA', 'AUTO'])
        
        console.print(Panel(
            Align.center(Text("INDIAN MARKET SUMMARY", style="bold bright_cyan")),
            style="on #0a0a0a",
            border_style="cyan"
        ))
        
        table = Table(
            show_header=True,
            header_style="bold bright_cyan on #0f3460",
            border_style="cyan",
            box=box.ROUNDED,
            expand=True
        )
        
        table.add_column("Category", style="bold bright_white", width=25)
        table.add_column("Total", justify="center", width=8)
        table.add_column("Gainers", justify="center", style="bright_green", width=10)
        table.add_column("Losers", justify="center", style="bright_red", width=10)
        table.add_column("Avg Change %", justify="right", width=15)
        table.add_column("Sentiment", justify="center", width=12)
        
        for cat_key, cat_data in summary.items():
            # Color code sentiment
            if cat_data['sentiment'] == 'BULLISH':
                sentiment_style = "bold bright_green"
            elif cat_data['sentiment'] == 'BEARISH':
                sentiment_style = "bold bright_red"
            else:
                sentiment_style = "bold bright_yellow"
            
            # Color code avg change
            if cat_data['avg_change_pct'] > 0:
                change_style = "bold bright_green"
            elif cat_data['avg_change_pct'] < 0:
                change_style = "bold bright_red"
            else:
                change_style = "bright_white"
            
            table.add_row(
                cat_data['name'],
                str(cat_data['total']),
                str(cat_data['gainers']),
                str(cat_data['losers']),
                Text(f"{cat_data['avg_change_pct']:+.2f}%", style=change_style),
                Text(cat_data['sentiment'], style=sentiment_style)
            )
        
        console.print(table)
        console.print("\n[bold bright_cyan]Press Enter to return to menu...[/]")
        input()
    
    def show_stock_search(self):
        """Interactive stock search"""
        console.clear()
        
        console.print(Panel(
            Align.center(Text("STOCK SEARCH", style="bold bright_cyan")),
            style="on #0a0a0a",
            border_style="cyan"
        ))
        
        query = Prompt.ask("\n[bold bright_cyan]Enter stock symbol or name[/]")
        
        with console.status(f"[bold bright_cyan]Searching for '{query}'...", spinner="dots"):
            matches = self.india_engine.search_stocks(query)
        
        if not matches:
            console.print(f"\n[bold bright_red]No stocks found matching '{query}'[/]")
        else:
            console.print(f"\n[bold bright_green]Found {len(matches)} matches:[/]\n")
            
            table = Table(show_header=True, border_style="cyan", box=box.ROUNDED, expand=True)
            table.add_column("Symbol", style="bold bright_white", width=15)
            table.add_column("Category", style="bright_cyan", width=30)
            table.add_column("Type", style="bright_yellow", width=15)
            
            for match in matches:
                table.add_row(
                    match['symbol'],
                    match['category'],
                    match['type']
                )
            
            console.print(table)
        
        console.print("\n[bold bright_cyan]Press Enter to return to menu...[/]")
        input()
    
    def show_coverage_stats(self):
        """Display coverage statistics"""
        console.clear()
        
        stats = self.india_engine.get_coverage_stats()
        
        console.print(Panel(
            Align.center(Text("COVERAGE STATISTICS", style="bold bright_cyan")),
            style="on #0a0a0a",
            border_style="cyan"
        ))
        
        # Main stats
        main_table = Table(show_header=False, box=box.SIMPLE, border_style="cyan")
        main_table.add_column("Metric", style="bold bright_white", width=20)
        main_table.add_column("Count", justify="right", style="bold bright_yellow", width=10)
        
        main_table.add_row("Total Stocks", str(stats['total_stocks']))
        main_table.add_row("NIFTY 50", str(stats['nifty_50']))
        main_table.add_row("NIFTY Next 50", str(stats['nifty_next_50']))
        main_table.add_row("Midcap", str(stats['midcap']))
        
        console.print(Panel(main_table, title="[bold bright_yellow]MAIN COVERAGE[/]", border_style="yellow"))
        
        # Sectoral coverage
        sector_table = Table(show_header=False, box=box.SIMPLE, border_style="cyan")
        sector_table.add_column("Sector", style="bold bright_white", width=15)
        sector_table.add_column("Count", justify="right", style="bold bright_cyan", width=10)
        
        for sector, count in stats['sectoral'].items():
            sector_table.add_row(sector.upper(), str(count))
        
        console.print(Panel(sector_table, title="[bold bright_cyan]SECTORAL COVERAGE[/]", border_style="cyan"))
        
        console.print(f"\n[bold bright_green]Available Categories:[/] {', '.join(stats['categories'])}")
        console.print("\n[bold bright_cyan]Press Enter to  return to menu...[/]")
        input()
    
    def run(self):
        """Main terminal loop"""
        while True:
            try:
                choice = self.show_main_menu()
                
                if choice == "1":
                    # Run crisis detection simulation
                    from terminal_ui import FinanceTerminalUI
                    crisis_ui = FinanceTerminalUI()
                    crisis_ui.run_simulation()
                
                elif choice == "2":
                    self.show_indian_stocks_live('NIFTY_50')
                
                elif choice == "3":
                    self.show_indian_stocks_live(sector='BANK')
                
                elif choice == "4":
                    self.show_indian_stocks_live(sector='IT')
                
                elif choice == "5":
                    self.show_stock_search()
                
                elif choice == "6":
                    self.show_market_summary()
                
                elif choice == "7":
                    self.show_coverage_stats()
                
                elif choice == "Q":
                    console.print("\n[bold bright_green]Thank you for using Finance-X Terminal![/]")
                    break
                    
            except KeyboardInterrupt:
                console.print("\n\n[bold bright_yellow]Returning to main menu...[/]")
                time.sleep(1)
            except Exception as e:
                console.print(f"\n[bold bright_red]Error: {e}[/]")
                console.print("\n[bold bright_cyan]Press Enter to continue...[/]")
                input()

if __name__ == "__main__":
    console.clear()
    terminal = EnhancedFinanceTerminal()
    terminal.run()
