"""Registra metadados de diagnóstico sem reproduzir dados da requisição."""

import logging


class SafeLogFormatter(logging.Formatter):
    def format(self, record):
        summary = f"{record.levelname} {record.name}"
        status = getattr(record, "status_code", None)
        if type(status) is int and 100 <= status <= 599:
            return f"{summary} status={status}"
        return summary
