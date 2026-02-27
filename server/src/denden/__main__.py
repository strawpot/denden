"""Entry point for `python -m denden` and `denden-server` CLI."""
from __future__ import annotations

import argparse
import logging
import os


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="denden-server",
        description="denden communication server",
    )
    parser.add_argument(
        "--addr",
        default=os.environ.get("DENDEN_ADDR", "127.0.0.1:9700"),
        help="listen address (default: 127.0.0.1:9700)",
    )
    parser.add_argument(
        "--load-module",
        action="append",
        default=[],
        dest="modules",
        help="Python module to load (can be repeated)",
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="enable debug logging",
    )
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )

    from denden.server import DenDenServer

    server = DenDenServer(addr=args.addr)

    for mod_path in args.modules:
        import importlib
        mod = importlib.import_module(mod_path)
        if hasattr(mod, "module"):
            instance = mod.module
        elif hasattr(mod, "create_module"):
            instance = mod.create_module()
        else:
            raise ValueError(
                f"module {mod_path} must expose 'module' or 'create_module'"
            )
        for method_name, handler in instance.methods().items():
            server._servicer.set_handler(method_name, handler)
        instance.on_load(server)

    server.run()


if __name__ == "__main__":
    main()
