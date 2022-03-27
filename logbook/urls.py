from django.urls import path
from . import views
from .views import LogDetailView, LogCreateView, LogUpdateView, LogDeleteView, LogListView


urlpatterns = [
    path('', LogListView.as_view(), name='logbook'),
    path('add/', LogCreateView.as_view(), name='log-add'),
    path('<int:pk>/', LogDetailView.as_view(), name='log-detail'),
    path('<int:pk>/update/', LogUpdateView.as_view(), name='log-update'),
    path('<int:pk>/remove/', LogDeleteView.as_view(), name='log-remove'),
]