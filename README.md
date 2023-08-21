# Project work: "Async Read-Only API for Online Cinema".

API to search Online cinema content. Entry point for clients.


## Stack
- REST API
- Python + FastAPI
- ASGI(guvicorn)
- ElasticSearch
- Redis for caсhe
- pytest
- Docker

Docker-compose.yaml to run all components: Elastic Search, Redis, Nginx.


## API documentation

[Swagger](http://127.0.0.1/api/openapi)


## Style guide
- [PEP8](https://peps.python.org/pep-0008/)  +  [Google Style Guide](https://google.github.io/styleguide/pyguide.html)


## Deploy

Clone repo:
```
git clone git@github.com:snesterkov/Async_API_sprint_1.git
```
Copy file:
```
cp .env.example .env
```
Edit .env file.

### DEV Deploy
```
sudo make dev
```
In DEV mode:
- API under ASGI Uvicorn with tracking of changes in the source code
- Migration of a movie database from SQLite (sql-loader) to Postgres

### PROD Deploy
```
sudo make up
```
or detach mode
```
sudo make up_detach
```

### Run tests
```
sudo make test
```
Elastic Search and Redis test instances are being raised in the tests.


Tests are compiled for all endpoints:
- boundary cases on data validation;
- pagination of data;
- full-text search;
- cache-aware search in Redis (checking the requested data directly in Redis).
