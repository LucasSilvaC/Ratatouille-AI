"""Exporta o PostgreSQL para um arquivo age sem gravar o dump em claro."""

import argparse
import os
from pathlib import Path
import subprocess
import tempfile


def backup(destination, recipient):
    if not os.environ.get("PGDATABASE") or not os.environ.get("PGUSER"):
        raise ValueError("Defina PGDATABASE e PGUSER para selecionar o banco e a credencial.")

    temporary_path = None
    try:
        with tempfile.NamedTemporaryFile(
            dir=destination.parent, prefix=".backup-", delete=False
        ) as encrypted:
            temporary_path = Path(encrypted.name)
            with subprocess.Popen(
                ["pg_dump", "--format=custom", "--no-password"],
                stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL,
            ) as dump:
                try:
                    result = subprocess.run(
                        ["age", "--encrypt", "--recipient", recipient],
                        stdin=dump.stdout,
                        stdout=encrypted,
                        stderr=subprocess.DEVNULL,
                        check=False,
                    )
                finally:
                    dump.stdout.close()

                dump_status = dump.wait()
            if result.returncode or dump_status:
                raise RuntimeError(
                    f"Backup falhou (pg_dump={dump_status}, age={result.returncode})."
                )
            encrypted.flush()
            os.fsync(encrypted.fileno())

        os.link(temporary_path, destination)
    finally:
        if temporary_path is not None:
            temporary_path.unlink(missing_ok=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("destination", type=Path)
    parser.add_argument("--recipient", required=True, help="Chave pública age do destinatário.")
    args = parser.parse_args()
    try:
        backup(args.destination, args.recipient)
    except FileExistsError:
        parser.exit(1, "O arquivo de destino já existe.\n")
    except FileNotFoundError:
        parser.exit(1, "Confirme o diretório de destino e a instalação de pg_dump e age.\n")
    except (OSError, ValueError, RuntimeError) as error:
        parser.exit(1, f"{error}\n")
