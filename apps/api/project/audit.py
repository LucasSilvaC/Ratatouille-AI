"""Correlação HTTP e auditoria das operações da API."""

import logging
from uuid import uuid4

from django.core.exceptions import ImproperlyConfigured
from django.db import DatabaseError
from django.utils.functional import SimpleLazyObject


logger = logging.getLogger("api.audit")

_ACCOUNT_AND_ANSWER_EVENTS = {
    ("token_obtain_pair", "POST"): "account.login",
    ("token_refresh", "POST"): "account.token_refresh",
    ("register", "POST"): "account.register",
    ("trocar-senha", "POST"): "account.password_change",
    ("redefinir-senha", "POST"): "account.password_reset_request",
    ("redefinir-senha-confirmar", "POST"): "account.password_reset_confirm_submit",
    ("usuario-list", "GET"): "account.list",
    ("usuario-detail", "GET"): "account.read",
    ("usuario-detail", "PUT"): "account.update",
    ("usuario-detail", "PATCH"): "account.update",
    ("usuario-detail", "DELETE"): "account.delete",
    ("resposta-list", "GET"): "answer.list",
    ("resposta-list", "POST"): "answer.create",
    ("resposta-detail", "GET"): "answer.read",
    ("resposta-detail", "PUT"): "answer.update",
    ("resposta-detail", "PATCH"): "answer.update",
    ("resposta-detail", "DELETE"): "answer.delete",
}

_STAFF_RESOURCES = {
    "classe": "catalog.class",
    "alimento": "catalog.food",
    "nutriente": "catalog.nutrient",
    "alimento-nutriente": "catalog.food_nutrient",
    "pergunta": "question",
}

_STAFF_EVENTS = {
    (f"{resource}-{route}", method): f"{event_prefix}.{action}"
    for resource, event_prefix in _STAFF_RESOURCES.items()
    for route, method, action in (
        ("list", "POST", "create"),
        ("detail", "PUT", "update"),
        ("detail", "PATCH", "update"),
        ("detail", "DELETE", "delete"),
    )
}

_EVENTS = {**_ACCOUNT_AND_ANSWER_EVENTS, **_STAFF_EVENTS}
_FAILED_REQUEST_EVENT = "request.failed"
AUDIT_EVENTS = frozenset(_EVENTS.values()) | {_FAILED_REQUEST_EVENT}
FAILURE_CODES = frozenset({
    "configuration_error", "database_error", "smtp_send_failed", "unexpected_error",
})


class RequestAuditMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.request_id = uuid4().hex
        response = self.get_response(request)
        response.headers["X-Request-ID"] = request.request_id

        match = request.resolver_match
        event = None
        if match and match.namespace == "api":
            event = _EVENTS.get((match.url_name, request.method))
        if response.status_code >= 500 and request.path_info.startswith("/api/"):
            event = event or _FAILED_REQUEST_EVENT
        if event is not None:
            self._audit(request, response, event)
        return response

    def process_exception(self, request, exception):
        if isinstance(exception, DatabaseError):
            request.audit_failure_code = "database_error"
        elif isinstance(exception, ImproperlyConfigured):
            request.audit_failure_code = "configuration_error"

    def _audit(self, request, response, event):
        status_code = response.status_code
        metadata = {
            "event": event,
            "request_id": request.request_id,
            "status_code": status_code,
        }
        failure_code = getattr(response, "audit_failure_code", None)
        if status_code >= 500:
            failure_code = getattr(request, "audit_failure_code", "unexpected_error")
        if failure_code:
            metadata["failure_code"] = failure_code
        if event == _FAILED_REQUEST_EVENT and request.resolver_match:
            metadata["route"] = request.resolver_match.url_name
        user = getattr(request, "user", None)
        # O DRF já atribui o usuário autenticado ao HttpRequest. Evite
        # resolver uma sessão Django apenas por causa do log.
        if type(user) is not SimpleLazyObject:
            actor_id = getattr(user, "pk", None)
            if type(actor_id) is int:
                metadata["actor_id"] = actor_id
        level = logging.ERROR if failure_code else logging.INFO
        logger.log(level, "API audit", extra=metadata)
