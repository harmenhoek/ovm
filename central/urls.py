from django.urls import path
from .views import (
    PostListView,

)
from . import views

urlpatterns = [
    path('', PostListView.as_view(), name='central-home'),
    path('post/<slug:postslug>/', PostListView.as_view(), name='post-detail'),
    # path('post/new/', PostCreateView.as_view(), name='post-create'),
    # path('post/<int:pk>/update/', PostUpdateView.as_view(), name='post-update'),
    # path('post/<int:pk>/delete/', PostDeleteView.as_view(), name='post-delete'),
    path('about/', views.about, name='central-about'),
]
