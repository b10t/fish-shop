import time

import requests
from environs import Env


class Moltin():
    __moltin_token = {}
    __moltin_client_id = ''

    def __new__(cls, moltin_client_id=''):
        try:
            if not cls.__moltin_client_id:
                cls.__moltin_client_id = moltin_client_id

            it = cls.__it__
        except AttributeError:
            it = cls.__it__ = object.__new__(cls)
        return it

    def __repr__(self):
        return '<{}>'.format(self.__class__.__name__.upper())

    def __eq__(self, other):
        return other is self

    def is_token_expired(self):
        """Проверка, истек ли срок действия токена."""
        if not self.__moltin_token:
            return True

        token_expires = self.__moltin_token.get('expires', 0)

        return time.time() > token_expires

    def get_access_token(self):
        """Возвращает токен."""
        if self.is_token_expired():
            data = {
                'client_id': self.__moltin_client_id,
                'grant_type': 'implicit',
            }

            response = requests.post(
                'https://api.moltin.com/oauth/access_token',
                data=data
            )
            response.raise_for_status()

            self.__moltin_token = response.json()

        return self.__moltin_token

    def get_or_create_cart(self, cart_id):
        """Создаёт корзину."""
        if cart := self.get_cart(cart_id):
            return cart

        moltin_token = self.get_access_token()

        headers = {
            'Authorization': f'Bearer {moltin_token.get("access_token")}'
        }

        payload = {
            'data': {
                'id': cart_id,
                'name': f'My cart ({cart_id})',
            }
        }

        response = requests.post(
            'https://api.moltin.com/v2/carts',
            headers=headers,
            json=payload
        )
        response.raise_for_status()

        return response.json()

    def get_cart(self, cart_id):
        """Получает данные корзины."""
        moltin_token = self.get_access_token()

        headers = {
            'Authorization': f'Bearer {moltin_token.get("access_token")}'
        }

        response = requests.get(
            f'https://api.moltin.com/v2/carts/{cart_id}',
            headers=headers,
        )
        response.raise_for_status()

        return response.json()

    def get_cart_items(self, cart_id):
        """Получает содержимое корзины."""
        moltin_token = self.get_access_token()

        headers = {
            'Authorization': f'Bearer {moltin_token.get("access_token")}'
        }

        response = requests.get(
            f'https://api.moltin.com/v2/carts/{cart_id}/items',
            headers=headers,
        )
        response.raise_for_status()

        return response.json()

    def add_cart_item(self, cart_id, item_id, quantity=1):
        """Добавляет товар в корзину."""
        moltin_token = self.get_access_token()

        headers = {
            'Authorization': f'Bearer {moltin_token.get("access_token")}'
        }

        payload = {
            'data': {
                'id': item_id,
                'type': 'cart_item',
                'quantity': int(quantity)
            }
        }

        response = requests.post(
            f'https://api.moltin.com/v2/carts/{cart_id}/items',
            headers=headers,
            json=payload
        )
        response.raise_for_status()

        return response.json()

    def remove_cart_item(self, cart_id, item_id):
        """Удаляет товар из корзины."""
        moltin_token = self.get_access_token()

        headers = {
            'Authorization': f'Bearer {moltin_token.get("access_token")}'
        }

        response = requests.delete(
            f'https://api.moltin.com/v2/carts/{cart_id}/items/{item_id}',
            headers=headers,
        )
        response.raise_for_status()

        return response.json()

    def get_products(self):
        """Возвращает список товаров."""
        products = []
        moltin_token = self.get_access_token()

        headers = {
            'Authorization': f'Bearer {moltin_token.get("access_token")}'
        }

        response = requests.get(
            'https://api.moltin.com/v2/products',
            headers=headers
        )
        response.raise_for_status()

        products = response.json().get('data', [])

        return products

    def get_product(self, item_id):
        """Возвращает описание товара."""
        moltin_token = self.get_access_token()

        headers = {
            'Authorization': f'Bearer {moltin_token.get("access_token")}'
        }

        response = requests.get(
            f'https://api.moltin.com/v2/products/{item_id}',
            headers=headers
        )
        response.raise_for_status()

        return response.json().get('data', {})

    def get_file_url(self, file_id):
        """Получает URL файла по id."""
        moltin_token = self.get_access_token()

        headers = {
            'Authorization': f'Bearer {moltin_token.get("access_token")}'
        }

        response = requests.get(
            f'https://api.moltin.com/v2/files/{file_id}',
            headers=headers
        )
        response.raise_for_status()

        return response.json()

    def create_customer(self, customer_id, customer_email):
        """Создает покупателя."""
        moltin_token = self.get_access_token()

        headers = {
            'Authorization': f'Bearer {moltin_token.get("access_token")}'
        }

        payload = {
            'data': {
                'type': 'customer',
                'name': f'{customer_id}',
                'email': f'{customer_email}'
            }
        }

        response = requests.post(
            f'https://api.moltin.com/v2/customers',
            headers=headers,
            json=payload
        )
        response.raise_for_status()

        return response.json()
