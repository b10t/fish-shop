# Бот по продаже рыбы в Telegram  

Бот позволяет продавать рыбу через мессенджер Telegram.  

Назначение программ:  
- tg_bot.py: чат-бот для Telegram.  

### Как установить

Python3 должен быть уже установлен.
Затем используйте `pip` (или `pip3`, есть конфликт с Python2) для установки зависимостей:
```bash
pip install -r requirements.txt
```

### Первоначальная настройка

Скопируйте файл `.env.Example` и переименуйте его в `.env`.  

Заполните переменные окружения в файле `.env`:  
`TELEGRAM_TOKEN` - токен телеграм бота.  
`MOLTIN_CLIENT_ID` - ID клиента сервиса Moltin.  
`REDIS_HOST` - адрес сервера Redis.  
`REDIS_PORT` - порт сервера Redis.  
`REDIS_USERNAME` - имя пользователя для сервера Redis.  
`REDIS_PASSWORD` - пароль пользователя для сервера Redis.  

### Как запускать

Для запуска чат-бота Telegram:  
```bash
python tg_bot.py
```

## Запуск, используя docker  

Docker должен быть установлен на локальную машину.  

Для сборки образа, используем команду:  
```bash
docker build --pull --rm -f "Dockerfile" -t fish_shop:latest "."
```

Для запуска контейнера, необходимо запустить команду:  
```bash
docker run --restart=always --detach --env-file .env --name=fish_shop fish_shop:latest
```

## Пример использования бота

[FishShopBot](https://t.me/FishShop_b10t_bot)

## Цель проекта

Код написан в образовательных целях на онлайн-курсе для веб-разработчиков [dvmn.org](https://dvmn.org/modules/)
