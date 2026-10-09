from django.urls import path
from .views import (
    MenuListView,
    OrderListCreateView,
    OrderDetailView,
    AddOrderItemView,
    RemoveOrderItemView,
    OrderStatusView,
)

urlpatterns = [
    path('menu/', MenuListView.as_view(), name='menu-list'),
    path('orders/', OrderListCreateView.as_view(), name='order-list-create'),
    path('orders/<int:pk>/', OrderDetailView.as_view(), name='order-detail'),
    path('orders/<int:pk>/add-item/', AddOrderItemView.as_view(), name='add-item'),
    path('orders/<int:pk>/items/<int:item_id>/', RemoveOrderItemView.as_view(), name='remove-item'),
    path('orders/<int:pk>/status/', OrderStatusView.as_view(), name='order-status'),
]
