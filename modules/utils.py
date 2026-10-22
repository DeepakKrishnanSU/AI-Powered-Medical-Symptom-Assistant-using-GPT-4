"""
utils.py - Formatting and UI Utilities for Medical Symptom Assistant.
Provides clean terminal styling, status spinners, banners, and table displays with safe Windows encoding.
"""

import sys
from typing import List, Dict, Any, Optional

# Ensure UTF-8 output on Windows consoles if supported
try:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    from rich.text import Text
    RICH_AVAILABLE = True
    console = Console(safe_box=True)
except ImportError:
    RICH_AVAILABLE = False
    console = None


def print_banner(title: str, subtitle: Optional[str] = None):
    """Prints a styled banner for terminal headers."""
    line = "=" * 68
    print(f"\n{line}")
    print(f" {title.center(66)} ")
    if subtitle:
        print(f" {subtitle.center(66)} ")
    print(f"{line}\n")


def print_section(title: str, icon: str = "[*]"):
    """Prints a prominent section header."""
    header = f"{icon} {title.upper()}"
    print(f"\n{header}")
    print("-" * (len(header) + 4))


def print_warning(message: str):
    """Prints a warning or escalation notification."""
    print(f"\n[!] WARNING / ESCALATION NOTICE:\n{message}\n")


def print_info(message: str):
    """Prints an informational note."""
    print(f"[i] {message}")


def print_success(message: str):
    """Prints a success message."""
    print(f"[+] {message}")


def display_key_value(pairs: Dict[str, Any], title: Optional[str] = None):
    """Renders key-value data cleanly in a list."""
    if title:
        print(f"\n[{title}]")
    for k, v in pairs.items():
        val_str = ", ".join(v) if isinstance(v, list) else str(v)
        print(f"  * {k:<24}: {val_str}")


def display_bullet_list(items: List[str], title: Optional[str] = None, bullet: str = "*"):
    """Displays a list of bullet points cleanly."""
    if title:
        print_section(title)
    if not items:
        print("  (None identified)")
        return
    for item in items:
        print(f"  {bullet} {item}")


def display_disclaimer():
    """Renders the required non-diagnostic medical disclaimer box."""
    disclaimer_text = (
        "======================================================================\n"
        "DISCLAIMER\n"
        "----------------------------------------------------------------------\n"
        "This AI-generated response is intended for educational and informational\n"
        "purposes only. It is not a medical diagnosis and does not replace\n"
        "professional evaluation, diagnosis, or treatment from a qualified healthcare\n"
        "provider.\n\n"
        "If you are experiencing severe, worsening, or urgent symptoms\n"
        "(such as severe chest pain, extreme breathlessness, or loss of consciousness),\n"
        "seek appropriate professional medical care immediately.\n"
        "======================================================================"
    )
    print(f"\n{disclaimer_text}\n")
