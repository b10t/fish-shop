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
    def get_products(cls):
        """Возвращает список продуктов."""
        moltin_token = cls.get_access_token()

        headers = {
            'Authorization': f'Bearer {moltin_token.get("access_token")}'
        }

        response = requests.get(
            'https://api.moltin.com/v2/products',
            headers=headers
        )
        response.raise_for_status()

        return response.json()

    @classmethod
    def add_cart_item(cls, cart_id, item_id):
        """Добавляет товар в корзину."""
        moltin_token = cls.get_access_token()

        headers = {
            'Authorization': f'Bearer {moltin_token.get("access_token")}'
        }

        payload = {
            'data': {
                'id': '536e9f8d-f197-4686-b0d4-...',
                'type': 'cart_item',
                'quantity': 1
            }
        }

        response = requests.post(
            'https://api.moltin.com/v2/carts/39f242e47f49.../items',
            headers=headers,
            json=payload
        )
        response.raise_for_status()

        return response.json()

# asd = Moltin.get_access_token()
# print(asd)

# asd = Moltin.get_products()
# print(asd)
