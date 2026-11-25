from django.test import SimpleTestCase, override_settings
from django.urls import path
from rest_framework.response import Response
from rest_framework.views import APIView


class DefaultPermissionView(APIView):
    def get(self, request):
        return Response()


def failed_view(request):
    raise RuntimeError("internal-diagnostic-value")


class CustomErrorView(APIView):
    permission_classes = ()

    def get(self, request):
        return Response({"detail": "internal-diagnostic-value"}, status=400, exception=True)


urlpatterns = [
    path("api/default-permission/", DefaultPermissionView.as_view()),
    path("api/failure/", failed_view),
    path("api/custom-error/", CustomErrorView.as_view()),
]


class ApiErrorContractTests(SimpleTestCase):
    def test_unauthenticated_request_has_safe_correlated_error(self):
        response = self.client.get("/api/respostas/")

        self.assertEqual(response.status_code, 401)
        self.assertTrue(response["WWW-Authenticate"].startswith("Bearer"))
        self.assertEqual(response.json()["code"], "not_authenticated")
        self.assertEqual(response.json()["request_id"], response["X-Request-ID"])

    def test_invalid_body_identifies_field_without_echoing_input(self):
        response = self.client.post(
            "/api/redefinir_senha/", {"email": "private-value"}, content_type="application/json"
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["fields"], {"email": ["invalid"]})
        self.assertNotIn(b"private-value", response.content)

    def test_malformed_json_does_not_echo_the_body(self):
        response = self.client.post(
            "/api/redefinir_senha/", '{"email": "private-value"', content_type="application/json"
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["code"], "parse_error")
        self.assertNotIn(b"private-value", response.content)

    @override_settings(ROOT_URLCONF=__name__)
    def test_manually_returned_drf_error_uses_the_safe_fallback(self):
        response = self.client.get("/api/custom-error/")

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["code"], "bad_request")
        self.assertNotIn(b"internal-diagnostic-value", response.content)

    @override_settings(DEBUG=True)
    def test_unknown_api_url_does_not_expose_debug_page(self):
        response = self.client.get("/api/nao-existe/")

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json()["code"], "not_found")
        self.assertEqual(response.json()["request_id"], response["X-Request-ID"])

    @override_settings(ROOT_URLCONF=__name__)
    def test_new_drf_view_requires_authentication_by_default(self):
        response = self.client.get("/api/default-permission/")
        self.assertEqual(response.status_code, 401)

    @override_settings(ROOT_URLCONF=__name__, DEBUG=True)
    def test_unexpected_error_is_sanitized_even_in_debug(self):
        self.client.raise_request_exception = False
        response = self.client.get("/api/failure/")

        self.assertEqual(response.status_code, 500)
        self.assertEqual(response.json()["code"], "internal_error")
        self.assertEqual(response.json()["request_id"], response["X-Request-ID"])
        self.assertNotIn(b"internal-diagnostic-value", response.content)

    @override_settings(PUBLIC_DEPLOYMENT=True)
    def test_public_mode_disables_api_documentation(self):
        for url in ("/api/schema/", "/api/swagger/"):
            with self.subTest(url=url):
                self.assertEqual(self.client.get(url).status_code, 403)
        self.assertEqual(self.client.get("/api/health/").status_code, 200)

    def test_local_schema_describes_bearer_authentication(self):
        response = self.client.get("/api/schema/", HTTP_ACCEPT="application/vnd.oai.openapi+json")

        self.assertEqual(response.status_code, 200)
        schema = response.json()
        self.assertEqual(schema["components"]["securitySchemes"]["jwtAuth"]["scheme"], "bearer")
        self.assertEqual(schema["paths"]["/api/respostas/"]["get"]["security"], [{"jwtAuth": []}])
