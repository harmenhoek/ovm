from django.urls import path
from .views import (
    PostListView,
    UsersView,
    UserDetailView,
    UserUpdateView,
    UserCreateView,
    PostMapView,
    PostOccupationView,
    PostInfoView,
    # PlanningModify
)
from . import views

urlpatterns = [
    path('', PostListView.as_view(), name='central-home'),
    path('post/<slug:postslug>/', PostListView.as_view(), name='post-detail'),
    path('post_map/', PostMapView.as_view(), name='post-map'),
    path('post_info/<slug:postslug>/', PostInfoView.as_view(), name='post-info'),
    path('post_occupation/<slug:postslug>/', PostOccupationView.as_view(), name='post-occupation'),
    path('about/', views.about, name='central-about'),
    path('personen/', UsersView.as_view(), name='users'),
    path('user/', UsersView.as_view(), name='users'),
    path('user/<int:pk>/', UserDetailView.as_view(), name='user-detail'),
    path('user/add/', UserCreateView.as_view(), name='user-add'),
    path('user/<int:pk>/update/', UserUpdateView.as_view(), name='user-update'),
    path('planning/<int:pk>/approve/', views.planning_approve, name='planning-approve'),
    path('planning/<int:pk>/remove/', views.planning_remove, name='planning-remove'),
    path('planning/<int:pk>/signoff/', views.planning_signoff, name='planning-signoff'),
    path('planning/<int:pk>/modify/', views.planning_modify, name='planning-modify'),
    path('planning/add/<int:pk>/', views.planning_add_dashboard, name='planning-add'),
    path('planning/add/', views.planning_add_dashboard, name='planning-add'),
    path('import/', views.importer, name='importer'),
    # path('planning/<int:pk>/modify/', PlanningModify.as_view(), name='planning-modify'),

 ]
