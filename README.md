# Проект: Асинхронный Read-only API для кинотеатра. 

Является точкой входа для всех клиентов. 

## Используемые технологии
- Протокол REST API
- Код приложения на Python + FastAPI.
- Приложение запускается под управлением сервера ASGI(guvicorn).
- В качестве хранилища используется ElasticSearch.
- Для кеширования используется Redis.
- Для функционального тестирования используется pytest
- Все компоненты системы запускаются через Docker: Elastic Search, Redix, Nginx.

## Ссылка на репозиторий

[IAmIrina](https://github.com/IAmIrina/Async_API_sprint_2.git)

## Внешняя Swager Документация

[Swagger](http://127.0.0.1/api/openapi)

## Style guide
Минимум, который необходимо соблюдать:
- [PEP8](https://peps.python.org/pep-0008/)  +  [Google Style Guide](https://google.github.io/styleguide/pyguide.html)


## Инструкция по разворачиванию сервиса

Склонировать репозиторий
```
git clone git@github.com:snesterkov/Async_API_sprint_1.git
```
Скопировать файл:  
```
cp .env.example .env
```
Отредактировать переменные окружения в файле .env любимым редактором. 

### Развернуть сервис в режиме DEV
```
sudo make dev
```
В режими DEV запускается:
- API под управлением сервера ASGI Uvicorn с отслеживаем изменений в исходном коде.
- Сервис переноса данных из SQLite (sql-loader)

### Развернуть сервис в режиме PROD
```
sudo make up
```
или в detach режиме
```
sudo make up_detach
```

### Запустить тесты
```
sudo make test
```
В тестах поднимается тестовые инстансы Elastic Search и Redis.

Тесты составлены для всех endpoints:
- граничные случаи по валидации данных;
- пагинация данных;
- полнотекстовый поиск;
- поиск с учётом кеша в Redis (проверка запрошенных данных напрямую в Redis).
