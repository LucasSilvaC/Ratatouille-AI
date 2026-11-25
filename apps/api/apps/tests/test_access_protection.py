from django.core.cache import cache
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import AccessToken


class AccessProtectionTests(APITestCase):
    def setUp(self):
        cache.clear()
        self.addCleanup(cache.clear)

    def test_account_routes_limit_requests_independently(self):
        for path, limit in (
            ("/api/token/", 10),
            ("/api/register/", 5),
            ("/api/token/refresh/", 30),
        ):
            with self.subTest(path=path):
                for _ in range(limit):
                    self.assertEqual(self.client.post(path, {}).status_code, 400)

                response = self.client.post(path, {})
                self.assertEqual(response.status_code, 429)
                self.assertIn("Retry-After", response)

    def test_access_token_expires_after_fifteen_minutes(self):
        token = AccessToken()
        self.assertEqual(token["exp"] - token["iat"], 15 * 60)
