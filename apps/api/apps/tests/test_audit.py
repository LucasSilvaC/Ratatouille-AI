import logging
from smtplib import SMTPException

from django.contrib.auth import get_user_model
from django.core.mail.backends.base import BaseEmailBackend
from django.db import OperationalError
from django.test import SimpleTestCase, override_settings
from django.urls import include, path, reverse
from rest_framework.test import APIClient, APITestCase


def failing_view(_request):
    raise RuntimeError("private profile data")


def unavailable_database(_request):
    raise OperationalError("private connection details")


urlpatterns = [
    path("api/", include(([
        path("unexpected/", failing_view, name="unexpected"),
        path("database/", unavailable_database, name="database"),
    ], "api"))),
]


class FailingEmailBackend(BaseEmailBackend):
    def send_messages(self, email_messages):
        raise SMTPException("private delivery details")


class RequestAuditTests(SimpleTestCase):
    client_class = APIClient

    def test_api_generates_its_own_correlation_id_for_each_request(self):
        url = reverse("api:health")
        first = self.client.get(url, headers={"X-Request-ID": "a" * 32})
        second = self.client.get(url, headers={"X-Request-ID": "a" * 32})

        self.assertRegex(first.headers.get("X-Request-ID", ""), r"^[0-9a-f]{32}$")
        self.assertNotEqual(first.headers["X-Request-ID"], "a" * 32)
        self.assertNotEqual(first.headers["X-Request-ID"], second.headers["X-Request-ID"])

    def test_rejected_password_change_records_event_status_actor_and_correlation_id(self):
        self.client.force_authenticate(user=get_user_model()(pk=42))

        with self.assertLogs("api.audit", logging.INFO) as captured:
            response = self.client.post(reverse("api:trocar-senha"), {}, format="json")

        self.assertEqual(response.status_code, 400)
        event, = captured.records
        self.assertEqual(event.event, "account.password_change")
        self.assertEqual(event.status_code, 400)
        self.assertEqual(event.actor_id, 42)
        self.assertEqual(event.request_id, response.headers["X-Request-ID"])

    @override_settings(ROOT_URLCONF=__name__, DEBUG=False)
    def test_unexpected_api_failure_has_a_safe_correlation_event(self):
        self.client.raise_request_exception = False

        with self.assertLogs("api.audit", logging.ERROR) as captured:
            response = self.client.get(reverse("api:unexpected"))

        self.assertEqual(response.status_code, 500)
        event, = captured.records
        self.assertEqual(event.event, "request.failed")
        self.assertEqual(event.route, "unexpected")
        self.assertEqual(event.failure_code, "unexpected_error")
        self.assertEqual(event.request_id, response.headers["X-Request-ID"])
        self.assertIsNone(event.exc_info)
        self.assertNotIn("private profile data", event.getMessage())

    @override_settings(ROOT_URLCONF=__name__)
    def test_database_failure_has_a_safe_reason_code(self):
        self.client.raise_request_exception = False

        with self.assertLogs("api.audit", logging.ERROR) as captured:
            response = self.client.get(reverse("api:database"))

        self.assertEqual(response.status_code, 500)
        event, = captured.records
        self.assertEqual(event.failure_code, "database_error")
        self.assertEqual(event.route, "database")
        self.assertEqual(event.request_id, response.headers["X-Request-ID"])
        self.assertIsNone(event.exc_info)


class LoginAuditTests(APITestCase):
    def test_successful_login_records_only_the_authenticated_internal_account_id(self):
        user = get_user_model().objects.create_user(username="pilot-user", password="sample-password")

        with self.assertLogs("api.audit", logging.INFO) as captured:
            response = self.client.post(
                reverse("api:token_obtain_pair"),
                {"username": "pilot-user", "password": "sample-password"},
                format="json",
            )

        self.assertEqual(response.status_code, 200)
        event, = captured.records
        self.assertEqual(event.event, "account.login")
        self.assertEqual(event.status_code, 200)
        self.assertEqual(event.actor_id, user.pk)
        self.assertEqual(event.request_id, response.headers["X-Request-ID"])
        self.assertNotIn(user.username, event.getMessage())

    @override_settings(EMAIL_BACKEND=__name__ + ".FailingEmailBackend")
    def test_reset_delivery_failure_is_correlated_without_changing_public_response(self):
        user = get_user_model().objects.create_user(
            username="test-user", email="test-user@example.test", password="sample-password"
        )
        url = reverse("api:redefinir-senha")

        with self.assertLogs("api.audit", logging.ERROR) as captured:
            response = self.client.post(url, {"email": user.email}, format="json")

        self.assertEqual(response.status_code, 202)
        self.assertEqual(response.json(), self.client.post(
            url, {"email": "unknown@example.test"}, format="json"
        ).json())
        event, = captured.records
        self.assertEqual(event.failure_code, "smtp_send_failed")
        self.assertEqual(event.request_id, response.headers["X-Request-ID"])
        self.assertIsNone(event.exc_info)
