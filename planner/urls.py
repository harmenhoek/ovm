from django.urls import path
from . import views

urlpatterns = [
    path('', views.planner, name='planner'),
    path('day/<slug:dayname>/', views.planner, name='planner'),
    path('planner_table/day/<slug:dayname>/', views.plannertable, name='planner-table'),
    path('modify/<int:pk>', views.planner_modify, name='planner-modify'),
    path('modify/<int:pk>/<int:start>/<int:end>/', views.planner_modify, name='planner-modify'),
    path('add/occupation', views.add_occupation, name='occupation-add'),
    path('add/occupation/<int:pk>/', views.add_occupation, name='occupation-add'),
    path('add/planning', views.add_planning, name='planner-add'),
    path('add/planning/<int:pk>/', views.add_planning, name='planner-add'),
 ]