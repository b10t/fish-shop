import time

import requests
from environs import Env


class Moltin():
    __moltin_token = {}

    @classmethod
    def is_token_expired(cls):
        """Проверка, истек ли срок действия токена."""
        if not cls.__moltin_token:
            return True

        token_expires = cls.__moltin_token.get('expires', 0)

        if time.time() > token_expires:
            return True

        return False

    @classmethod
    def get_access_token(cls):
        """Возвращает токен."""
        if cls.is_token_expired():
            env = Env()
            env.read_env()

            moltin_client_id = env.str('MOLTIN_CLIENT_ID')

            data = {
                'client_id': moltin_client_id,
                'grant_type': 'implicit',
            }

            response = requests.post(
                'https://api.moltin.com/oauth/access_token',
                data=data
            )
            response.raise_for_status()

            cls.__moltin_token = response.json()

        return cls.__moltin_token

    @classmethod
    def create_cart(cls, cart_id):
        """Создаёт корзину."""
        if cart := cls.get_cart(cart_id):
            return cart

        moltin_token = cls.get_access_token()

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

    @classmethod
    def get_cart(cls, cart_id):
        """Получает данные корзины."""
        try:
            moltin_token = cls.get_access_token()

            headers = {
                'Authorization': f'Bearer {moltin_token.get("access_token")}'
            }

            response = requests.get(
                f'https://api.moltin.com/v2/carts/{cart_id}',
                headers=headers,
            )
            response.raise_for_status()

            return response.json()
        except Exception:
            return {}

    @classmethod
    def get_cart_items(cls, cart_id):
        """Получает содержимое корзины."""
        try:
            moltin_token = cls.get_access_token()

            headers = {
                'Authorization': f'Bearer {moltin_token.get("access_token")}'
            }

            response = requests.get(
                f'https://api.moltin.com/v2/carts/{cart_id}/items',
                headers=headers,
            )
            response.raise_for_status()

            return response.json()
        except Exception:
            return {}

    @classmethod
    def add_cart_item(cls, cart_id, item_id, quantity=1):
        """Добавляет товар в корзину."""
        moltin_token = cls.get_access_token()

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

    @classmethod
    def remove_cart_item(cls, cart_id, item_id):
        """Удаляет товар из корзины."""
        moltin_token = cls.get_access_token()

        headers = {
            'Authorization': f'Bearer {moltin_token.get("access_token")}'
        }

        response = requests.delete(
            f'https://api.moltin.com/v2/carts/{cart_id}/items/{item_id}',
            headers=headers,
        )
        response.raise_for_status()

        return response.json()

    @classmethod
    def get_products(cls):
        """Возвращает список товаров."""
        products = []
        moltin_token = cls.get_access_token()

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

    @classmethod
    def get_product(cls, item_id):
        """Возвращает описание товара."""
        moltin_token = cls.get_access_token()

        headers = {
            'Authorization': f'Bearer {moltin_token.get("access_token")}'
        }

        response = requests.get(
            f'https://api.moltin.com/v2/products/{item_id}',
            headers=headers
        )
        response.raise_for_status()

        return response.json().get('data', {})

    @classmethod
    def get_file_url(cls, file_id):
        """Получает URL файла по id."""
        moltin_token = cls.get_access_token()

        headers = {
            'Authorization': f'Bearer {moltin_token.get("access_token")}'
        }

        response = requests.get(
            f'https://api.moltin.com/v2/files/{file_id}',
            headers=headers
        )
        response.raise_for_status()

        return response.json()

    @classmethod
    def create_customer(cls, customer_id, customer_email):
        """Создает покупателя."""
        moltin_token = cls.get_access_token()

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
