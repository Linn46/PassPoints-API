from typing import Any


def print_section(title: str) -> None:
    print()
    print("=" * 72)
    print(title)
    print("=" * 72)


def print_step(
    name: str,
    status: str = "OK",
) -> None:
    symbol = "✓" if status == "OK" else "✗"

    print(f"  {symbol} {name}")


def print_value(
    label: str,
    value: Any,
) -> None:
    print(f"    {label}: {value}")


def print_result(
    label: str,
    value: Any,
) -> None:
    print()
    print(f"  RESULTADO: {label}")
    print(f"  {value}")