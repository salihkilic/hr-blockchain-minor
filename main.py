# Entry point for the HR Blockchain minor demo application.
# Provides a minimal DearPyGui UI bootstrap that loads the blockchain explorer view.

try:
    from ui import build_ui
except ImportError as e:  # pragma: no cover - critical import failure
    raise SystemExit(f"Failed to import UI layer: {e}")


if __name__ == '__main__':
    # Launch the DearPyGui based interface.
    build_ui()
