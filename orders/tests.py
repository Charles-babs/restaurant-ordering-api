from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status

from .models import MenuItem, Order, OrderItem


User = get_user_model()


class RestaurantAPITests(APITestCase):

    def setUp(self):
        # Create two normal customers
        self.customer1 = User.objects.create_user(
            username='customer1',
            password='testpass123'
        )

        self.customer2 = User.objects.create_user(
            username='customer2',
            password='testpass123'
        )

        # Create a staff user
        self.staff = User.objects.create_user(
            username='staff',
            password='testpass123',
            is_staff=True
        )

        # Create menu items
        self.available_item = MenuItem.objects.create(
            name='Jollof Rice',
            description='Nigerian jollof rice',
            price='3000.00',
            category='Rice',
            is_available=True
        )

        self.unavailable_item = MenuItem.objects.create(
            name='Fried Rice',
            description='Fried rice',
            price='3500.00',
            category='Rice',
            is_available=False
        )

        # Create an order belonging to customer1
        self.order = Order.objects.create(
            customer=self.customer1
        )

        self.order_item = OrderItem.objects.create(
            order=self.order,
            menu_item=self.available_item,
            quantity=2
        )

    def test_customer_can_place_order_with_available_item(self):
        self.client.force_authenticate(user=self.customer2)

        response = self.client.get(
            f'/api/orders/{self.order.id}/'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND
        )

    def test_unavailable_menu_item_cannot_be_ordered(self):
        self.client.force_authenticate(user=self.customer1)

        data = {
            'items': [
                {
                    'menu_item': self.unavailable_item.id,
                    'quantity': 1
                }
            ]
        }

        response = self.client.post(
            '/api/orders/',
            data,
            format='json'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )

    def test_customer_cannot_change_order_status(self):
        self.client.force_authenticate(user=self.customer1)

        response = self.client.patch(
            f'/api/orders/{self.order.id}/status/',
            {'status': 'preparing'},
            format='json'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN
        )

    def test_staff_can_change_pending_order_to_preparing(self):
        self.client.force_authenticate(user=self.staff)

        response = self.client.patch(
            f'/api/orders/{self.order.id}/status/',
            {'status': 'preparing'},
            format='json'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.order.refresh_from_db()

        self.assertEqual(
            self.order.status,
            'preparing'
        )

    def test_invalid_status_transition_is_rejected(self):
        self.client.force_authenticate(user=self.staff)

        response = self.client.patch(
            f'/api/orders/{self.order.id}/status/',
            {'status': 'completed'},
            format='json'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )
