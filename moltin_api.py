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
                'quantity': quantity
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


# asd = Moltin.get_access_token()
# print(asd)


# asd = Moltin.get_product('5259b9c9-9008-4ff3-9d76-81f9e2a6aedc')
# print(asd)

# asd = Moltin.download_file('f1efe08e-9206-4ee8-8899-b378c50dff2a')
# print(asd)
