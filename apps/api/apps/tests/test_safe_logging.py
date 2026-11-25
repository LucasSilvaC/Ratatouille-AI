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
