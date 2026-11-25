"""Registra metadados de diagnóstico sem reproduzir dados da requisição."""

import logging
import re
from datetime import UTC, datetime

from .audit import AUDIT_EVENTS, FAILURE_CODES


_REQUEST_ID = re.compile(r"[0-9a-f]{32}")
_ROUTE_NAME = re.compile(r"[a-zA-Z0-9_-]{1,80}")


class SafeLogFormatter(logging.Formatter):
    def format(self, record):
        fields = [record.levelname, record.name]
        status = getattr(record, "status_code", None)
        if type(status) is int and 100 <= status <= 599:
            fields.append(f"status={status}")
        if record.name == "api.audit":
            event = getattr(record, "event", None)
            request_id = getattr(record, "request_id", None)
            if type(event) is str and event in AUDIT_EVENTS:
                fields.append(f"event={event}")
            if type(request_id) is str and _REQUEST_ID.fullmatch(request_id):
                fields.append(f"request_id={request_id}")
            failure_code = getattr(record, "failure_code", None)
            if type(failure_code) is str and failure_code in FAILURE_CODES:
                fields.append(f"failure_code={failure_code}")
            route = getattr(record, "route", None)
            if event == "request.failed" and type(route) is str and _ROUTE_NAME.fullmatch(route):
                fields.append(f"route={route}")
            actor_id = getattr(record, "actor_id", None)
            if type(actor_id) is int and actor_id > 0:
                fields.append(f"actor_id={actor_id}")
            timestamp = datetime.fromtimestamp(record.created, UTC)
            fields.append(f"timestamp={timestamp.isoformat(timespec='milliseconds')}")
        return " ".join(fields)
