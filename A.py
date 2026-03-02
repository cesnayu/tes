"""
╔══════════════════════════════════════════════════════════╗
║         STOCK VALUATION DASHBOARD - Python CLI           ║
║         Menggunakan yfinance + rich untuk tampilan        ║
╚══════════════════════════════════════════════════════════╝

Install dependencies:
    pip install yfinance rich

Cara pakai:
    python stock_dashboard.py               → mode interaktif
    python stock_dashboard.py AAPL          → langsung cari 1 saham
    python stock_dashboard.py AAPL MSFT BBCA.JK  → banyak saham sekaligus
"""

import sys
import math
import yfinance as yf
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich.columns import Columns
from rich import box
from rich.prompt import Prompt
from rich.rule import Rule
from datetime import datetime

console = Console()


# ─────────────────────────────────────────────────────────
# Helper Functions
# ─────────────────────────────────────────────────────────

def fmt(val, decimals=2, suffix=""):
    """Format angka, return 'N/A' jika None/NaN."""
    if val is None or (isinstance(val, float) and math.isnan(val)):
        return "[dim]N/A[/dim]"
    return f"{val:.{decimals}f}{suffix}"

def fmt_large(val):
    """Format angka besar ke T/B/M."""
    if val is None or (isinstance(val, float) and math.isnan(val)):
        return "[dim]N/A[/dim]"
    if abs(val) >= 1e12:
        return f"{val/1e12:.2f}T"
    if abs(val) >= 1e9:
        return f"{val/1e9:.2f}B"
    if abs(val) >= 1e6:
        return f"{val/1e6:.2f}M"
    return f"{val:.2f}"

def badge_per(val):
    """PER: rendah = baik (undervalued)."""
    if val is None or (isinstance(val, float) and math.isnan(val)):
        return "[dim]—[/dim]"
    if val <= 15:   return "[bold green]● Murah[/bold green]"
    if val <= 30:   return "[bold yellow]● Wajar[/bold yellow]"
    return "[bold red]● Mahal[/bold red]"

def badge_pbv(val):
    """PBV: < 1 = murah."""
    if val is None or (isinstance(val, float) and math.isnan(val)):
        return "[dim]—[/dim]"
    if val <= 1:    return "[bold green]● Murah[/bold green]"
    if val <= 3:    return "[bold yellow]● Wajar[/bold yellow]"
    return "[bold red]● Mahal[/bold red]"

def badge_roe(val_pct):
    """ROE %: tinggi = baik."""
    if val_pct is None or (isinstance(val_pct, float) and math.isnan(val_pct)):
        return "[dim]—[/dim]"
    if val_pct >= 20:   return "[bold green]● Tinggi[/bold green]"
    if val_pct >= 10:   return "[bold yellow]● Sedang[/bold yellow]"
    if val_pct > 0:     return "[bold red]● Rendah[/bold red]"
    return "[bold red]● Negatif[/bold red]"

def badge_roa(val_pct):
    """ROA %: tinggi = baik."""
    if val_pct is None or (isinstance(val_pct, float) and math.isnan(val_pct)):
        return "[dim]—[/dim]"
    if val_pct >= 15:   return "[bold green]● Tinggi[/bold green]"
    if val_pct >= 5:    return "[bold yellow]● Sedang[/bold yellow]"
    if val_pct > 0:     return "[bold red]● Rendah[/bold red]"
    return "[bold red]● Negatif[/bold red]"

def badge_der(val):
    """DER: rendah = lebih aman."""
    if val is None or (isinstance(val, float) and math.isnan(val)):
        return "[dim]—[/dim]"
    if val <= 0.5:  return "[bold green]● Aman[/bold green]"
    if val <= 1.5:  return "[bold yellow]● Sedang[/bold yellow]"
    return "[bold red]● Tinggi[/bold red]"

def badge_eps(val):
    if val is None or (isinstance(val, float) and math.isnan(val)):
        return "[dim]—[/dim]"
    if val > 5:     return "[bold green]● Tinggi[/bold green]"
    if val > 0:     return "[bold yellow]● Positif[/bold yellow]"
    return "[bold red]● Negatif[/bold red]"

def badge_yield(val_pct):
    if val_pct is None or (isinstance(val_pct, float) and math.isnan(val_pct)):
        return "[dim]—[/dim]"
    if val_pct >= 7:    return "[bold green]● Tinggi[/bold green]"
    if val_pct >= 3:    return "[bold yellow]● Sedang[/bold yellow]"
    return "[bold red]● Rendah[/bold red]"

def safe(val):
    """Return None jika NaN."""
    if val is None:
        return None
    try:
        if math.isnan(float(val)):
            return None
    except (TypeError, ValueError):
        return None
    return val


# ─────────────────────────────────────────────────────────
# Core: Fetch & Parse Data
# ─────────────────────────────────────────────────────────

def fetch_stock_data(ticker: str) -> dict:
    """Ambil semua data dari Yahoo Finance."""
    info = yf.Ticker(ticker).info

    if not info or info.get("regularMarketPrice") is None:
        raise ValueError(f"Ticker '{ticker}' tidak ditemukan atau tidak ada data.")

    currency = info.get("currency", "USD")
    price    = safe(info.get("regularMarketPrice") or info.get("currentPrice"))

    # EPS
    eps = safe(info.get("trailingEps"))

    # PER
    pe = safe(info.get("trailingPE") or info.get("forwardPE"))

    # PBV
    pbv = safe(info.get("priceToBook"))

    # ROE
    roe = safe(info.get("returnOnEquity"))
    roe_pct = roe * 100 if roe is not None else None

    # ROA
    roa = safe(info.get("returnOnAssets"))
    roa_pct = roa * 100 if roa is not None else None

    # DER
    total_debt   = safe(info.get("totalDebt"))
    total_equity = safe(info.get("totalStockholderEquity") or info.get("bookValue"))
    shares       = safe(info.get("sharesOutstanding"))
    if total_equity and shares and not isinstance(total_equity, float):
        pass  # already absolute
    elif total_equity and shares:
        pass
    book_val_per_share = safe(info.get("bookValue"))
    # Reconstruct equity from bookValue * shares jika perlu
    if total_equity is None and book_val_per_share and shares:
        total_equity = book_val_per_share * shares

    der = None
    if total_debt is not None and total_equity and total_equity != 0:
        der = total_debt / total_equity

    # Revenue Per Share (RPS)
    total_revenue = safe(info.get("totalRevenue"))
    rps = None
    if total_revenue and shares and shares != 0:
        rps = total_revenue / shares

    # Earning Yield
    earning_yield = None
    if pe and pe != 0:
        earning_yield = (1 / pe) * 100

    return {
        "ticker":        ticker.upper(),
        "name":          info.get("longName") or info.get("shortName", ticker),
        "sector":        info.get("sector", "—"),
        "industry":      info.get("industry", "—"),
        "exchange":      info.get("exchange", ""),
        "currency":      currency,
        "price":         price,
        "prev_close":    safe(info.get("previousClose")),
        "change_pct":    safe(info.get("regularMarketChangePercent")) or
                         ((price - info.get("previousClose", price)) / max(info.get("previousClose", price), 1) * 100
                          if price and info.get("previousClose") else None),
        "market_cap":    safe(info.get("marketCap")),
        "week52_high":   safe(info.get("fiftyTwoWeekHigh")),
        "week52_low":    safe(info.get("fiftyTwoWeekLow")),
        "div_yield":     safe(info.get("dividendYield")),
        "eps":           eps,
        "pe":            pe,
        "pbv":           pbv,
        "roe_pct":       roe_pct,
        "roa_pct":       roa_pct,
        "der":           der,
        "rps":           rps,
        "earning_yield": earning_yield,
        "total_revenue": total_revenue,
        "shares":        shares,
    }


# ─────────────────────────────────────────────────────────
# Display Functions
# ─────────────────────────────────────────────────────────

def display_single(d: dict):
    """Tampilkan dashboard lengkap untuk 1 saham."""
    currency = d["currency"]
    is_idr   = currency == "IDR"

    # ── Header ──
    price_str = fmt_large(d["price"]) if is_idr else fmt(d["price"])
    chg = d["change_pct"]
    if chg is not None:
        sign  = "+" if chg >= 0 else ""
        color = "green" if chg >= 0 else "red"
        chg_str = f"  [{color}]{sign}{chg:.2f}%[/{color}]"
    else:
        chg_str = ""

    header = Text()
    header.append(f"{d['name']}\n", style="bold white")
    header.append(f"{d['ticker']}  ·  {d['exchange']}  ·  {currency}\n", style="dim cyan")
    header.append(f"{currency} {price_str}", style="bold cyan")
    header.append(chg_str)
    if d["sector"] != "—":
        header.append(f"\n{d['sector']}  ·  {d['industry']}", style="dim")

    console.print(Panel(header, border_style="cyan", padding=(1, 2)))

    # ── Valuasi ──
    console.print(Rule("[bold cyan]📊 Metrik Valuasi & Profitabilitas[/bold cyan]", style="cyan"))

    table = Table(
        box=box.ROUNDED,
        border_style="dim",
        header_style="bold cyan",
        show_lines=True,
        expand=True,
    )
    table.add_column("Metrik",      style="bold white", width=22)
    table.add_column("Nilai",       justify="right",    width=18)
    table.add_column("Keterangan",  style="dim",        width=45)
    table.add_column("Rating",      justify="center",   width=20)

    # Rows
    def rps_val():
        if d["rps"] is None:
            return "[dim]N/A[/dim]"
        return fmt_large(d["rps"]) if is_idr else fmt(d["rps"])

    rows = [
        (
            "EPS",
            fmt(d["eps"]),
            "Earnings Per Share – laba bersih per lembar saham",
            badge_eps(d["eps"]),
        ),
        (
            "PER",
            fmt(d["pe"], 1, "x") if d["pe"] else "[dim]N/A[/dim]",
            "Price-to-Earnings Ratio – harga vs laba",
            badge_per(d["pe"]),
        ),
        (
            "PBV",
            fmt(d["pbv"], 2, "x") if d["pbv"] else "[dim]N/A[/dim]",
            "Price-to-Book Value – harga vs nilai buku",
            badge_pbv(d["pbv"]),
        ),
        (
            "ROE",
            fmt(d["roe_pct"], 1, "%") if d["roe_pct"] is not None else "[dim]N/A[/dim]",
            "Return on Equity – imbal hasil ekuitas",
            badge_roe(d["roe_pct"]),
        ),
        (
            "ROA",
            fmt(d["roa_pct"], 1, "%") if d["roa_pct"] is not None else "[dim]N/A[/dim]",
            "Return on Assets – imbal hasil aset",
            badge_roa(d["roa_pct"]),
        ),
        (
            "DER",
            fmt(d["der"], 2, "x") if d["der"] is not None else "[dim]N/A[/dim]",
            "Debt-to-Equity Ratio – rasio utang vs ekuitas",
            badge_der(d["der"]),
        ),
        (
            "RPS",
            rps_val(),
            f"Revenue Per Share (Rev ÷ Shares)",
            "[cyan]Dihitung manual[/cyan]" if d["rps"] else "[dim]—[/dim]",
        ),
        (
            "Earning Yield",
            fmt(d["earning_yield"], 2, "%") if d["earning_yield"] else "[dim]N/A[/dim]",
            "Earning Yield = 1/PER × 100%",
            badge_yield(d["earning_yield"]),
        ),
    ]

    for metrik, nilai, ket, rating in rows:
        table.add_row(metrik, nilai, ket, rating)

    console.print(table)

    # ── Info Tambahan ──
    console.print(Rule("[bold white]📌 Info Tambahan[/bold white]", style="dim"))
    info_table = Table(box=box.SIMPLE, show_header=False, expand=True, padding=(0,2))
    info_table.add_column(style="dim", width=25)
    info_table.add_column(style="bold white", justify="right")
    info_table.add_column(style="dim", width=25)
    info_table.add_column(style="bold white", justify="right")

    mcap_str = fmt_large(d["market_cap"])
    div_str  = fmt(d["div_yield"] * 100 if d["div_yield"] else None, 2, "%")
    lo_str   = fmt_large(d["week52_low"]) if is_idr else fmt(d["week52_low"])
    hi_str   = fmt_large(d["week52_high"]) if is_idr else fmt(d["week52_high"])
    rev_str  = fmt_large(d["total_revenue"])
    shr_str  = fmt_large(d["shares"])

    info_table.add_row("Market Cap",       mcap_str, "Dividend Yield", div_str)
    info_table.add_row("52W Low",          lo_str,   "52W High",       hi_str)
    info_table.add_row("Total Revenue",    rev_str,  "Shares Out.",    shr_str)

    console.print(info_table)
    console.print()


def display_comparison(stocks: list[dict]):
    """Tampilkan tabel perbandingan beberapa saham."""
    console.print(Rule("[bold cyan]📊 Perbandingan Saham[/bold cyan]", style="cyan"))

    table = Table(
        box=box.ROUNDED,
        border_style="dim",
        header_style="bold cyan",
        show_lines=True,
    )
    table.add_column("Metrik",    style="bold white", width=18)
    for d in stocks:
        table.add_column(d["ticker"], justify="right", width=14)

    def row(label, values):
        table.add_row(label, *values)

    def get_vals(key, formatter):
        return [formatter(d.get(key)) for d in stocks]

    def fmt_pct(v):
        if v is None: return "[dim]N/A[/dim]"
        return fmt(v, 1, "%")

    def fmt_ratio(v):
        if v is None: return "[dim]N/A[/dim]"
        return fmt(v, 2, "x")

    def fmt_pe(v):
        if v is None: return "[dim]N/A[/dim]"
        return fmt(v, 1, "x")

    def fmt_eps_(v):
        if v is None: return "[dim]N/A[/dim]"
        return fmt(v, 2)

    currencies = [d["currency"] for d in stocks]

    # Price
    prices = []
    for d in stocks:
        if d["price"] is None:
            prices.append("[dim]N/A[/dim]")
        elif d["currency"] == "IDR":
            prices.append(fmt_large(d["price"]))
        else:
            prices.append(fmt(d["price"]))

    row("Harga",    prices)
    row("EPS",      get_vals("eps",        fmt_eps_))
    row("PER",      get_vals("pe",         fmt_pe))
    row("PBV",      get_vals("pbv",        fmt_ratio))
    row("ROE %",    get_vals("roe_pct",    fmt_pct))
    row("ROA %",    get_vals("roa_pct",    fmt_pct))
    row("DER",      get_vals("der",        fmt_ratio))
    row("Earn. Yield", get_vals("earning_yield", fmt_pct))

    console.print(table)
    console.print()


# ─────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────

def run(tickers: list[str]):
    console.print()
    console.print(Panel.fit(
        "[bold cyan]NILAI SAHAM[/bold cyan]  [dim]Stock Valuation Dashboard[/dim]",
        border_style="cyan",
        padding=(0, 2),
    ))
    console.print(f"[dim]  {datetime.now().strftime('%d %B %Y  %H:%M:%S')}[/dim]\n")

    results = []
    for ticker in tickers:
        ticker = ticker.upper().strip()
        with console.status(f"[cyan]Mengambil data {ticker}...[/cyan]"):
            try:
                data = fetch_stock_data(ticker)
                results.append(data)
                console.print(f"[green]✓[/green] {ticker} — {data['name']}")
            except Exception as e:
                console.print(f"[red]✗[/red] {ticker} — [red]{e}[/red]")

    if not results:
        console.print("\n[red]Tidak ada data yang berhasil diambil.[/red]")
        return

    console.print()

    if len(results) == 1:
        display_single(results[0])
    else:
        # Tampilkan detail masing-masing, lalu tabel perbandingan
        for d in results:
            display_single(d)
        if len(results) > 1:
            display_comparison(results)

    console.print("[dim]⚠️  Data dari Yahoo Finance. Bukan saran investasi.[/dim]\n")


def main():
    if len(sys.argv) > 1:
        tickers = sys.argv[1:]
        run(tickers)
    else:
        console.print(Panel.fit(
            "[bold cyan]NILAI SAHAM[/bold cyan]  [dim]Stock Valuation Dashboard[/dim]\n"
            "[dim]Ketik ticker saham, pisahkan dengan spasi untuk membandingkan.[/dim]\n"
            "[dim]Saham Indonesia: BBCA.JK  |  Keluar: q[/dim]",
            border_style="cyan",
        ))
        while True:
            try:
                inp = Prompt.ask("\n[cyan]Ticker[/cyan]").strip()
                if inp.lower() in ("q", "quit", "exit", "keluar"):
                    console.print("[dim]Sampai jumpa![/dim]")
                    break
                if not inp:
                    continue
                tickers = inp.split()
                run(tickers)
            except KeyboardInterrupt:
                console.print("\n[dim]Keluar.[/dim]")
                break


if __name__ == "__main__":
    main()
