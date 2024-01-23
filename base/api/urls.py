from django.urls import path
from . import views


# django does not know about this urls files
urlpatterns = [
    path('', views.getRoutes),
    path('rooms/',views.getRooms),
    path('rooms/<str:pk>',views.getRoom),

]