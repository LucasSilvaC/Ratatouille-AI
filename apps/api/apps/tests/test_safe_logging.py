import io
import logging
import sys

from django.test import SimpleTestCase


class SafeLoggingTests(SimpleTestCase):
    def test_http_log_contains_status_without_request_or_exception_details(self):
        logger = logging.getLogger("django.request")
        output = io.StringIO()
        handler = logging.StreamHandler(output)
        handler.setFormatter(logger.handlers[0].formatter)

        try:
            raise ValueError("resposta privada e senha")
        except ValueError:
            record = logger.makeRecord(
                logger.name, logging.ERROR, __file__, 1,
                "Falha em /api/redefinir_senha/token-secreto/", (), sys.exc_info(),
                extra={"status_code": 500},
            )
        handler.handle(record)

        self.assertEqual(output.getvalue(), "ERROR django.request status=500\n")

    def test_audit_logs_only_allowed_event_and_correlation_metadata(self):
        formatter = logging.getLogger("django.request").handlers[0].formatter
        logger = logging.getLogger("api.audit")
        record = logger.makeRecord(
            logger.name, logging.INFO, __file__, 1, "user@example.test", (), None,
            extra={
                "status_code": 204,
                "event": "answer.delete",
                "request_id": "a" * 32,
                "actor_id": 42,
                "raw_path": "/api/respostas/id-privado",
                "password": "senha",
                "failure_code": "private-token",
                "route": "private-route",
            },
        )
        record.created = 0

        self.assertEqual(
            formatter.format(record),
            f"INFO api.audit status=204 event=answer.delete request_id={'a' * 32} "
            "actor_id=42 timestamp=1970-01-01T00:00:00.000+00:00",
        )
