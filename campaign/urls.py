from django.urls import path

from . import views

app_name = "campaign"

urlpatterns = [
    path("", views.home, name="home"),
    path("reservar/", views.reserve_kilometers, name="reserve_kilometers"),
    path("km/<int:number>/", views.sponsor_kilometer, name="sponsor_kilometer"),
    path("km/<int:number>/detalhe/", views.kilometer_detail, name="kilometer_detail"),
    path("obrigado/", views.thank_you, name="thank_you"),
    path("painel/", views.panel, name="panel"),
    path("painel/login/", views.panel_login, name="panel_login"),
    path("painel/sair/", views.panel_logout, name="panel_logout"),
]
