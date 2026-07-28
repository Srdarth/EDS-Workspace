#!/usr/bin/env python3
"""EddY Scanner - Modulo de Percepcao
Varre diretorios e extrai metadados dos arquivos.
"""

import os
import sys
from datetime import datetime


def scan_directory(path="."):
    """Escaneia um diretorio e retorna lista de arquivos com metadados."""
    files = []
    for root, dirs, filenames in os.walk(path):
        for filename in filenames:
            filepath = os.path.join(root, filename)
            try:
                stat = os.stat(filepath)
                files.append({
                    "path": filepath,
                    "name": filename,
                    "size": stat.st_size,
                    "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                    "created": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                })
            except (OSError, PermissionError):
                continue
    return files


if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "."
    results = scan_directory(target)
    print(f"Encontrados {len(results)} arquivos em {target}")
    for f in results[:5]:
        print(f"  {f['name']} ({f['size']} bytes)")
