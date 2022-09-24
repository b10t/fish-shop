import requests

# Получаем токен

MOLTIN_CLIENT_ID = ''

data = {
    'client_id': MOLTIN_CLIENT_ID,
    'grant_type': 'implicit',
}

response = requests.post(
    'https://api.moltin.com/oauth/access_token', data=data)
response.raise_for_status()

moltin_token = response.json()

print(moltin_token.get('access_token'))

# Получаем список продуктов

headers = {
    'Authorization': f'Bearer {moltin_token.get("access_token")}'
}

# response = requests.get(
#     'https://api.moltin.com/v2/products',
#     headers=headers
# )
# response.raise_for_status()

# print(response.json())


# Создаем корзину
# payload = {
#     'data': {
#         'id': '39f242e47f49...',
#         'name': 'My cart',
#     }
# }

# response = requests.post(
#     'https://api.moltin.com/v2/carts',
#     headers=headers,
#     json=payload
# )
# response.raise_for_status()

# print(response.json())


# Добавляем продукт в корзину

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

print(response.json())
