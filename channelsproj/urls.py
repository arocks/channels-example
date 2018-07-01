from django.contrib import admin
from django.urls import path

from notifier.views import HomeView

urlpatterns = [
    path('', HomeView.as_view()),
    path('admin/', admin.site.urls),
]
