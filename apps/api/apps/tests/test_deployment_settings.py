import os
import subprocess
import sys
from pathlib import Path

from django.core.management.utils import get_random_secret_key
from django.test import SimpleTestCase


class PublicDeploymentSettingsTests(SimpleTestCase):
    def check_settings(self, **overrides):
        environment = {
            **os.environ,
            "DJANGO_PUBLIC_DEPLOYMENT": "true",
            "DJANGO_SECRET_KEY": get_random_secret_key(),
            "DJANGO_ALLOWED_HOSTS": "api.example.test",
            "DJANGO_DB_PASSWORD": get_random_secret_key(),
            "DJANGO_EMAIL_BACKEND": "django.core.mail.backends.smtp.EmailBackend",
            "DJANGO_EMAIL_USE_TLS": "true",
            **overrides,
        }
        return subprocess.run(
            [sys.executable, "-c", "import project.settings"],
            cwd=Path(__file__).resolve().parents[2],
            env=environment,
            capture_output=True,
            text=True,
            check=False,
        )

    def test_public_deployment_requires_an_explicit_secret_key(self):
        for secret in ("", "curta", "x" * 50, "django-insecure-" + get_random_secret_key()):
            with self.subTest(case=len(secret)):
                result = self.check_settings(DJANGO_SECRET_KEY=secret)

                self.assertNotEqual(result.returncode, 0)
                self.assertIn("DJANGO_SECRET_KEY", result.stderr)

    def test_public_deployment_only_accepts_explicit_domain_names(self):
        for hosts in (
            "", "localhost 127.0.0.1", "127.0.0.10", "*",
            "api.example.test .example.test", "https://api.example.test",
        ):
            with self.subTest(hosts=hosts):
                result = self.check_settings(DJANGO_ALLOWED_HOSTS=hosts)

                self.assertNotEqual(result.returncode, 0)
                self.assertIn("DJANGO_ALLOWED_HOSTS", result.stderr)

    def test_public_deployment_requires_a_non_default_database_password(self):
        for password in ("", "   ", "ratatouille_api", "ratatouille"):
            with self.subTest(case=len(password)):
                result = self.check_settings(DJANGO_DB_PASSWORD=password)

                self.assertNotEqual(result.returncode, 0)
                self.assertIn("DJANGO_DB_PASSWORD", result.stderr)

    def test_public_deployment_accepts_distinct_domains_and_credentials(self):
        result = self.check_settings(
            DJANGO_ALLOWED_HOSTS="api.example.test api-secondary.example.test",
        )

        self.assertEqual(result.returncode, 0, result.stderr)

    def test_local_mode_starts_without_public_deployment_credentials(self):
        result = self.check_settings(
            DJANGO_PUBLIC_DEPLOYMENT="false",
            DJANGO_SECRET_KEY="",
            DJANGO_ALLOWED_HOSTS="",
            DJANGO_DB_PASSWORD="ratatouille_api",
        )

        self.assertEqual(result.returncode, 0, result.stderr)

    def test_public_deployment_disables_non_smtp_email_backends(self):
        result = self.check_settings(
            DJANGO_EMAIL_BACKEND="django.core.mail.backends.console.EmailBackend",
        )

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("DJANGO_EMAIL_BACKEND", result.stderr)

    def test_public_deployment_requires_tls_for_smtp(self):
        result = self.check_settings(DJANGO_EMAIL_USE_TLS="false")

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("DJANGO_EMAIL_USE_TLS", result.stderr)
