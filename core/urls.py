from django.contrib.auth import views as auth_views
from django.urls import path

from . import views

urlpatterns = [
    path("", views.landing, name="landing"),
    path("register/", views.register, name="register"),
    path("login/", auth_views.LoginView.as_view(template_name="login.html"), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("go/", views.post_login_redirect, name="post_login_redirect"),

    path("dashboard/", views.user_dashboard, name="user_dashboard"),

    path("control/", views.admin_dashboard, name="admin_dashboard"),
    path("control/zones/", views.zone_list, name="zone_list"),
    path("control/zones/new/", views.zone_create, name="zone_create"),
    path("control/zones/<int:pk>/edit/", views.zone_edit, name="zone_edit"),
    path("control/zones/<int:pk>/delete/", views.zone_delete, name="zone_delete"),

    path("api/checkin/", views.api_checkin, name="api_checkin"),
    path("api/zones/", views.api_zones, name="api_zones"),
    path("api/entries/recent/", views.api_recent_entries, name="api_recent_entries"),
]
