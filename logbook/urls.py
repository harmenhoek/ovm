from django.urls import path
from . import views
from .views import LogDetailView, LogCreateView, LogUpdateView, LogDeleteView


urlpatterns = [
    path('', views.logbook, name='logbook'),
    path('day/<slug:dayname>/', views.logbook, name='logbook'),
    path('add/', LogCreateView.as_view(), name='log-add'),
    path('<int:pk>/', LogDetailView.as_view(), name='log-detail'),
    path('<int:pk>/update/', LogUpdateView.as_view(), name='log-update'),
    path('<int:pk>/remove/', LogDeleteView.as_view(), name='log-remove'),
    path('logtable/', views.logbooktable, name='log-table'),
    path('logtable/day/<slug:dayname>/', views.logbooktable, name='log-table'),
    # path('export/day/<slug:dayname>/', views.generatepdf, name='export'),
    path('exportpage/day/<slug:dayname>/', views.exportpage, name='export-page'),

]