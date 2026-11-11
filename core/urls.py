from django.contrib.auth import views as auth
from django.views.generic import RedirectView
from django.urls import path
from . import views as v

urlpatterns = [
    path("", v.home, name="home"),
    path("ingresar/", auth.LoginView.as_view(), name="login"),
    path("login/", RedirectView.as_view(pattern_name="login", permanent=False)),
    path("salir/", auth.LogoutView.as_view(), name="logout"),
    path("registro/<str:kind>/", v.register, name="register"),

    # Notificaciones comunes
    path("notificaciones/", v.notifications_list, name="notifications_list"),
    path("notificaciones/<int:pk>/leida/", v.mark_notification_read, name="mark_notification_read"),

    # Estudiante (HU01, HU02, HU03, HU04, HU05, HU12)
    path("ofertas/", v.offers, name="offers"),
    path("ofertas/<int:pk>/", v.offer_detail, name="offer_detail"),
    path("mis-postulaciones/", v.my_applications, name="my_applications"),
    path("postulaciones/<int:pk>/retirar/", v.withdraw, name="withdraw"),
    path("perfil/", v.profile, name="profile"),

    # Empresa (HU06, HU07, HU08, HU09)
    path("empresa/perfil/", v.company_profile, name="company_profile"),
    path("empresa/ofertas/", v.company_offers, name="company_offers"),
    path("empresa/ofertas/nueva/", v.offer_form, name="offer_new"),
    path("empresa/ofertas/<int:pk>/editar/", v.offer_form, name="offer_edit"),
    path("empresa/ofertas/<int:pk>/postulantes/", v.applicants, name="applicants"),
    path("empresa/ofertas/<int:pk>/comparar/", v.compare, name="compare"),
    path("empresa/ofertas/<int:pk>/<str:status>/", v.offer_status, name="offer_status"),

    # Administrador (HU10, HU11)
    path("panel/validaciones/", v.validations, name="validations"),
    path("panel/reportes/", v.reports, name="reports"),
    path("panel/usuarios/", v.admin_users, name="admin_users"),
    path("panel/usuarios/<int:pk>/estado/", v.admin_user_toggle, name="admin_user_toggle"),
    path("panel/usuarios/<int:pk>/eliminar/", v.admin_user_delete, name="admin_user_delete"),
    path("panel/areas/", v.admin_areas, name="admin_areas"),
    path("panel/areas/<int:pk>/editar/", v.admin_area_edit, name="admin_area_edit"),
    path("panel/areas/<int:pk>/eliminar/", v.admin_area_delete, name="admin_area_delete"),
]
