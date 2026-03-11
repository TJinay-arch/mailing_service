from django.urls import path

from .views import DashboardView, HomeAdvertiseView

app_name = "dashboard"

urlpatterns = [
    path("", DashboardView.as_view(), name="home"),
    path("home_advertise/", HomeAdvertiseView.as_view(), name="home_advertise"),
]
