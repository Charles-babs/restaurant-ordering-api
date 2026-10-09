from rest_framework import serializers
from django.db import transaction
from .models import MenuItem, Order, OrderItem


class MenuItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = MenuItem
        fields = [
            'id',
            'name',
            'description',
            'price',
            'category',
            'is_available'
        ]


class OrderItemCreateSerializer(serializers.Serializer):
    menu_item = serializers.PrimaryKeyRelatedField(
        queryset=MenuItem.objects.all()
    )
    quantity = serializers.IntegerField(min_value=1)

    def validate_menu_item(self, value):
        if not value.is_available:
            raise serializers.ValidationError(
                f"{value.name} is currently unavailable."
            )
        return value


class OrderItemSerializer(serializers.ModelSerializer):
    menu_item = MenuItemSerializer(read_only=True)

    class Meta:
        model = OrderItem
        fields = ['id', 'menu_item', 'quantity']


class OrderSerializer(serializers.ModelSerializer):
    customer = serializers.StringRelatedField(read_only=True)
    items = OrderItemSerializer(many=True, read_only=True)
    total = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        read_only=True
    )

    class Meta:
        model = Order
        fields = [
            'id',
            'customer',
            'status',
            'created_at',
            'items',
            'total'
        ]


class PlaceOrderSerializer(serializers.Serializer):
    items = OrderItemCreateSerializer(many=True)

    def validate_items(self, value):
        if not value:
            raise serializers.ValidationError(
                "An order must contain at least one item."
            )

        menu_item_ids = [item['menu_item'].id for item in value]

        if len(menu_item_ids) != len(set(menu_item_ids)):
            raise serializers.ValidationError(
                "Each menu item should appear only once."
            )

        return value

    @transaction.atomic
    def create(self, validated_data):
        request = self.context['request']

        order = Order.objects.create(
            customer=request.user
        )

        order_items = [
            OrderItem(
                order=order,
                menu_item=item['menu_item'],
                quantity=item['quantity']
            )
            for item in validated_data['items']
        ]

        OrderItem.objects.bulk_create(order_items)

        return order
