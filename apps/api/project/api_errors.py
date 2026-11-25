"""Contrato HTTP dos erros da API, sem copiar valores enviados pelo cliente."""

from django.http import JsonResponse
from rest_framework.exceptions import ValidationError
from rest_framework.views import exception_handler


HTTP_ERRORS = {
    400: ("bad_request", "Requisição inválida."),
    401: ("not_authenticated", "Autenticação válida é necessária."),
    403: ("permission_denied", "Operação não permitida."),
    404: ("not_found", "Recurso não encontrado."),
    405: ("method_not_allowed", "Método não permitido."),
    406: ("not_acceptable", "Formato de resposta indisponível."),
    409: ("conflict", "A operação conflita com o estado atual do recurso."),
    413: ("request_too_large", "Requisição excede o tamanho permitido."),
    415: ("unsupported_media_type", "Formato de requisição não suportado."),
    429: ("throttled", "Limite de requisições atingido."),
    500: ("internal_error", "Falha interna ao processar a requisição."),
    503: ("service_unavailable", "Serviço temporariamente indisponível."),
}


def error_payload(request, status_code):
    fallback = HTTP_ERRORS[500] if status_code >= 500 else HTTP_ERRORS[400]
    code, message = HTTP_ERRORS.get(status_code, fallback)
    return {"code": code, "message": message, "request_id": request.request_id}


def handle_api_exception(exc, context):
    response = exception_handler(exc, context)
    if response is None:
        return None

    payload = error_payload(context["request"], response.status_code)
    if isinstance(exc, ValidationError):
        payload["code"] = "validation_error"
        codes = exc.get_codes()
        payload["fields"] = codes if isinstance(codes, dict) else {"non_field_errors": codes}
    elif response.status_code < 500:
        payload["code"] = getattr(exc, "default_code", payload["code"])

    response.data = payload
    response.api_error_payload = payload
    response["Cache-Control"] = "no-store"
    return response


class ApiErrorMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if not request.path_info.startswith("/api/") or response.status_code < 400:
            return response

        headers = {
            name: value
            for name, value in response.items()
            if name.lower() not in {"content-type", "content-length", "content-encoding"}
        }
        payload = getattr(response, "api_error_payload", None)
        if payload is None:
            payload = error_payload(request, response.status_code)
        safe_response = JsonResponse(
            payload,
            status=response.status_code,
            headers=headers,
        )
        safe_response.cookies = response.cookies
        safe_response["Cache-Control"] = "no-store"
        return safe_response
