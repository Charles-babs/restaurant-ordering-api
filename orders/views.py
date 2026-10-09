from rest_framework.permissions import IsAdminUser
from .serializers import (
    OrderSerializer,
    PlaceOrderSerializer,
    OrderItemCreateSerializer,
)
from .models import Order, OrderItem
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import generics
from rest_framework.permissions import AllowAny
from .models import MenuItem
from .serializers import MenuItemSerializer


class MenuListView(generics.ListAPIView):
    serializer_class = MenuItemSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        return MenuItem.objects.filter(is_available=True)


class OrderListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        orders = Order.objects.filter(
            customer=request.user
        ).prefetch_related(
            'items__menu_item'
        ).order_by('-created_at')

        order_status = request.query_params.get('status')

        if order_status:
            valid_statuses = dict(Order.STATUS_CHOICES)

            if order_status not in valid_statuses:
                return Response(
                    {'error': 'Invalid order status.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            orders = orders.filter(status=order_status)

        serializer = OrderSerializer(
            orders,
            many=True
        )

        return Response(serializer.data)

    def post(self, request):
        serializer = PlaceOrderSerializer(
            data=request.data,
            context={'request': request}
        )

        if serializer.is_valid():
            order = serializer.save()
            response_serializer = OrderSerializer(order)
            return Response(
                response_serializer.data,
                status=status.HTTP_201_CREATED
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )


class OrderDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        order = get_object_or_404(
            Order.objects.prefetch_related('items__menu_item'),
            pk=pk,
            customer=request.user
        )

        serializer = OrderSerializer(order)
        return Response(serializer.data)


class AddOrderItemView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, pk):
        order = get_object_or_404(
            Order,
            pk=pk,
            customer=request.user
        )

        if order.status != 'pending':
            return Response(
                {'error': 'Items can only be added to pending orders.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = OrderItemCreateSerializer(data=request.data)

        if serializer.is_valid():
            data = serializer.validated_data
            menu_item = data['menu_item']
            quantity = data['quantity']

            existing_item = order.items.filter(
                menu_item=menu_item
            ).first()

            if existing_item:
                existing_item.quantity += quantity
                existing_item.save(update_fields=['quantity'])
            else:
                OrderItem.objects.create(
                    order=order,
                    menu_item=menu_item,
                    quantity=quantity
                )

            return Response(
                OrderSerializer(order).data,
                status=status.HTTP_200_OK
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )


class RemoveOrderItemView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, pk, item_id):
        order = get_object_or_404(
            Order,
            pk=pk,
            customer=request.user
        )

        if order.status != 'pending':
            return Response(
                {'error': 'Items can only be removed from pending orders.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        item = get_object_or_404(
            OrderItem,
            pk=item_id,
            order=order
        )

        item.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)



class OrderStatusView(APIView):
    permission_classes = [IsAdminUser]

    TRANSITIONS = {
        'pending': ['preparing', 'cancelled'],
        'preparing': ['ready'],
        'ready': ['completed'],
        'completed': [],
        'cancelled': [],
    }

    def patch(self, request, pk):
        order = get_object_or_404(Order, pk=pk)
        new_status = request.data.get('status')

        valid_statuses = dict(Order.STATUS_CHOICES)

        if new_status not in valid_statuses:
            return Response(
                {'error': 'Invalid order status.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if new_status not in self.TRANSITIONS[order.status]:
            return Response(
                {'error': f'Cannot change status from {order.status} to {new_status}.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        order.status = new_status
        order.save(update_fields=['status'])

        return Response(OrderSerializer(order).data)


