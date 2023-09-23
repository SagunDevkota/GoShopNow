# GoShopNow E-Commerce Backend

Welcome to the backend of the GoShopNow E-Commerce site. This README provides information on how to set up, configure, and run the backend services.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Getting Started](#getting-started)
3. [Configuration](#configuration)
4. [Running the Services](#running-the-services)
5. [Service Details](#service-details)
6. [Features](#features)
7. [Constraints](#constraints)

## Prerequisites

Before you begin, make sure you have the following tools installed on your system:

- Docker (version 24.0.2 or later)
- Docker Compose (version 2.19.1 or later)

## Getting Started

To get started with the GoShopNow backend, follow these steps:

1. Clone this repository to your local machine:

   ```bash
   git clone https://github.com/yourusername/goshopnow-backend.git
   cd goshopnow-backend
   ```

2. Create a .env file and configure the environment variables as needed.
    DB_HOST=
    DB_NAME=
    DB_USER=
    DB_PASS=
    KHALTI_API_KEY = 
    email = 
    password = 

    POSTGRES_DB=
    POSTGRES_USER=
    POSTGRES_PASSWORD=

    CELERY_BROKER = 
    CELERY_BACKEND =

3. Build the Docker container:
    ```
    docker-compose build
    ```

## Configuration
You can configure the backend services using environment variables in the .env file. Make sure to update this file with your specific configuration.

## Running the Services
Start the backend services using Docker Compose:
```
docker-compose up
```
The services will start, and you can access the GoShopNow backend API at `http://127.0.0.1:8000`.

## Service Details

### App
* Service Name: app
* Image: goshopnow:v1.0
* Ports: 8000 (HTTP API)
* Dependencies: db, redis, es

### Database (PostgreSQL)
* Service Name: db
* Image: postgres:13-alpine
* Ports: 5432 (PostgreSQL)
* Volume: dev-db-data

### Celery
* Service Name: celery
* Dependencies: redis
* Command: celery --app=app worker --loglevel=info --beat

### Redis
* Service Name: redis
* Image: redis:alpine

### Elasticsearch
* Service Name: es
* Image: elasticsearch:7.17.12
* Ports: 9200 (HTTP API)
* Volume: es_data

## Features
- User authentication, authorization and account activation using email
- Product management (add, edit, delete) from admin panel
- Shopping cart functionality
- Order processing and tracking
- Payment gateway integration(Khalti)
- Search functionality (using Elasticsearch)
- Background task processing with Celery
- Caching using Redis
- Restocking notification using email
- Reward points for each succesful purchase
- Discount coupon based on slot machine applied to total amount.
- Payment history tracking
- API documentation (Swagger) `http://127.0.0.1:8000/api/docs/#/`

## Constraints
- Currently supports only one instance of Elasticsearch (single-node).
- Limited support for product categories (expandable in future versions).
- Payment gateway integration limited to Khalti.
- Five images per product
- One delivery location per user

Please refer to the [Issues](https://github.com/SagunDevkota/GoShopNow/issues) section for known issues and planned improvements.
