"""Liga cada rota HTTP à view correspondente e dá nomes estáveis às rotas."""

from django.conf import settings
from django.contrib.auth.views import PasswordResetCompleteView
from django.http import JsonResponse
from django.urls import path
from django.views.decorators.http import require_safe
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from rest_framework.permissions import BasePermission

from .accounts import views as accounts_views
from .foods import views as foods_views
from .diagnosis import views as diagnosis_views


app_name = "api"


class LocalDocumentationPermission(BasePermission):
    def has_permission(self, request, view):
        return not settings.PUBLIC_DEPLOYMENT


@require_safe
def health(_request):
    return JsonResponse({"status": "ok"})


urlpatterns = [
    path("health/", health, name="health"),
    path(
        "schema/",
        SpectacularAPIView.as_view(
            authentication_classes=[], permission_classes=[LocalDocumentationPermission]
        ),
        name="schema",
    ),
    path(
        "swagger/",
        SpectacularSwaggerView.as_view(
            url_name="api:schema", authentication_classes=[],
            permission_classes=[LocalDocumentationPermission],
        ),
        name="swagger",
    ),
    path("token/", accounts_views.LoginAPIView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", accounts_views.RenovarTokenAPIView.as_view(), name="token_refresh"),
    path("register/", accounts_views.CriarUsuarioAPIView.as_view(), name="register"),
    path("senha/", accounts_views.TrocarSenhaAPIView.as_view(), name="trocar-senha"),
    path("usuarios/", accounts_views.UsuarioListView.as_view(), name="usuario-list"),
    path("usuarios/<int:pk>/", accounts_views.UsuarioDetailView.as_view(), name="usuario-detail"),
    path("redefinir_senha/", accounts_views.ResetPasswordAPIView.as_view(), name="redefinir-senha"),
    path(
        "redefinir_senha/<uidb64>/<token>/",
        accounts_views.ConfirmarRedefinicaoSenhaView.as_view(),
        name="redefinir-senha-confirmar",
    ),
    path(
        "redefinir_senha/concluida/",
        PasswordResetCompleteView.as_view(template_name="api/redefinir_senha_concluida.html"),
        name="redefinir-senha-concluida",
    ),
    path("classes/", foods_views.ClasseListCreateView.as_view(), name="classe-list"),
    path("classes/<int:pk>/", foods_views.ClasseDetailView.as_view(), name="classe-detail"),
    path("alimentos/", foods_views.AlimentoListCreateView.as_view(), name="alimento-list"),
    path("alimentos/<path:pk>/", foods_views.AlimentoDetailView.as_view(), name="alimento-detail"),
    path("nutrientes/", foods_views.NutrienteListCreateView.as_view(), name="nutriente-list"),
    path("nutrientes/<int:pk>/", foods_views.NutrienteDetailView.as_view(), name="nutriente-detail"),
    path(
        "alimentos-nutrientes/",
        foods_views.AlimentoNutrienteListCreateView.as_view(),
        name="alimento-nutriente-list",
    ),
    path(
        "alimentos-nutrientes/<int:pk>/",
        foods_views.AlimentoNutrienteDetailView.as_view(),
        name="alimento-nutriente-detail",
    ),
    path("perguntas/", diagnosis_views.PerguntaListCreateView.as_view(), name="pergunta-list"),
    path("perguntas/<str:pk>/", diagnosis_views.PerguntaDetailView.as_view(), name="pergunta-detail"),
    path("respostas/", diagnosis_views.RespostaListCreateView.as_view(), name="resposta-list"),
    path("respostas/<str:pk>/", diagnosis_views.RespostaDetailView.as_view(), name="resposta-detail"),
]
