
# BitcoinInfo

## Project Purpose

The **BitcoinInfo** project is a Flask-based application designed to retrieve and display information about the Bitcoin blockchain by interfacing with the Blockchain.info API. It runs in a Dockerized environment using a PostgreSQL database for storing relevant blockchain data. This application can be used to fetch and analyze blockchain data, and can be easily extended or integrated into other blockchain monitoring systems.

## Installation Guidelines

### Prerequisites

- Docker and Docker Compose installed
- PostgreSQL installed (optional if running without Docker)

### Steps

1. Clone the repository:

   ```bash
   git clone https://github.com/C0rwin/BitcoinInfo.git
   cd BitcoinInfo
   ```

2. Build and run the containers using Docker Compose:

   ```bash
   docker-compose up --build
   ```

   This will spin up both the PostgreSQL database and the Flask app in separate containers.

3. Verify the services are running by accessing `http://localhost:8080` with curl command.

## Running the Application

### Via Docker Compose

Once the application is running, you can interact with the API at:

- **Local Development**: `http://localhost:8080`
- **Production**: Set your environment to production mode by modifying `docker-compose.yaml`.

To stop the application:

```bash
docker-compose down
```

### Without Docker

If you prefer to run the app without Docker:

1. Install the necessary dependencies:

   ```bash
   pip install -r requirements.txt
   ```

2. Set up the PostgreSQL database as defined in `config.dev.yaml` or `config.prod.yaml`.

3. Run the application:

   ```bash
   python main.py
   ```

## Project Structure

```bash
.
├── db
    ├── model
        ├── cache.py       # Manages caching of blockchain API responses
    ├── database.py        # Defines the PostgreSQL database connection and interaction logic
├── config.py              # Handles application configuration, loading YAML files
├── config.dev.yaml        # Configuration file for development environment
├── config.prod.yaml       # Configuration file for production environment
├── database.py            # Defines the PostgreSQL database connection and interaction logic
├── bitcoin_info.py        # Core logic to fetch Bitcoin blockchain data from the API
├── server.py              # Handles HTTP server setup with Flask
├── main.py                # Entry point for starting the Flask application
├── Dockerfile             # Docker image setup for the Flask app
├── docker-compose.yaml    # Defines services for running the app and database in containers
```

# Code Structure

## Overview

The **BitcoinInfo** Flask app is designed to provide Bitcoin-related data by interacting with an external API and storing data in a PostgreSQL database. This document outlines the purpose of each class in the application, how they interconnect, and the overall architecture and design of the project.

## 1. Main Components

### `main.py`
- **Purpose**: This is the entry point of the Flask application.
- **Functionality**:
  - Initializes the Flask app.
  - Registers all the necessary routes.
  - Configures app settings (like caching and database connections).

### `server.py`
- **Purpose**: Responsible for defining routes and handling HTTP requests.
- **Functionality**:
  - Provides the API for the client to interact with the application.
  - Uses `bitcoin_info.py` to fetch data from the blockchain API.
  - Calls `database.py` to store or retrieve blockchain data.
  - Calls `cache.py` to store frequently used API responses.

### `bitcoin_info.py`
- **Purpose**: Handles communication with the Blockchain.info API to fetch Bitcoin-related data.
- **Functionality**:
  - Fetches information such as the latest Bitcoin block and transaction data.
  - Handles errors, retries, and API response processing.

### `database.py`
- **Purpose**: Manages all database interactions with PostgreSQL.
- **Functionality**:
  - Connects to the PostgreSQL database.
  - Stores block and transaction data.
  - Fetches previously stored blockchain data for analysis or display.

### `cache.py`
- **Purpose**: Implements a caching layer to store API responses temporarily.
- **Functionality**:
  - Stores data fetched from the blockchain API in memory to reduce API calls.
  - Returns cached data when available to reduce response times and API usage.

### `config.py`
- **Purpose**: Loads configuration settings from YAML files for different environments (development, production).
- **Functionality**:
  - Reads `config.dev.yaml` and `config.prod.yaml` based on the environment.
  - Provides configuration settings to the app such as API endpoints, database credentials, and retry limits.

## 2. Interconnections

- **`main.py`**: This is the central component that initializes the app. It sets up the server, database, and caching mechanisms.
- **`server.py`**: This defines all API endpoints and handles HTTP requests. It uses `bitcoin_info.py` to fetch data from the API and uses `database.py` to store or retrieve blockchain data.
- **`bitcoin_info.py`**: Responsible for fetching blockchain data from the Blockchain.info API and either caching the results in `cache.py` or storing them in `database.py`.
- **`database.py`**: Interacts with the PostgreSQL database to store and retrieve data related to Bitcoin blocks and transactions.
- **`cache.py`**: Provides a cache to store recently fetched API results, reducing the number of calls made to the external blockchain API.

## 3. Project Architecture Structure and Design

The project follows a modular structure with a separation of concerns, ensuring that each component handles a distinct responsibility. This design improves maintainability, scalability, and flexibility.

### Architecture Overview:
- **API Layer**: The HTTP API is exposed via Flask, and defined in `server.py`. This layer is responsible for receiving incoming HTTP requests, fetching the necessary data, and returning it as responses.
- **Service Layer**: The core business logic for fetching blockchain data resides in `bitcoin_info.py`. This file handles communication with external services like Blockchain.info.
- **Data Layer**: All database interactions are abstracted into `database.py`, ensuring that the core app logic does not need to handle raw SQL queries.
- **Caching Layer**: The `cache.py` layer reduces load on the API by caching frequently requested data.

### Key Design Patterns:
- **Separation of Concerns**: Each module (API, service, data, caching) is responsible for a specific part of the application, making the code easier to extend and debug.
- **Configuration Management**: Environment-specific configuration is handled via YAML files, allowing the app to easily switch between development and production modes.
- **Service-Oriented**: Each component provides a specific service, e.g., `bitcoin_info.py` for fetching data, `database.py` for storage, and `cache.py` for caching.

## 4. Class Relationships

Here’s a summary of how the classes interact with each other:

1. **`main.py`**: Initializes and ties together all components. It starts the Flask server (`server.py`) and manages the application's configuration.
2. **`server.py`**: Acts as the API interface. It uses:
   - **`bitcoin_info.py`** to fetch Bitcoin data from the API.
   - **`database.py`** to store or retrieve blockchain data.
   - **`cache.py`** to cache responses for frequently requested data.
3. **`bitcoin_info.py`**: Fetches blockchain data and interacts with both `cache.py` (to check for cached data or store new data) and `database.py` (to store data).
4. **`database.py`**: Manages the interaction with PostgreSQL. It stores or retrieves data based on requests from `server.py` and `bitcoin_info.py`.
5. **`cache.py`**: Provides a caching mechanism that stores recently fetched data and reduces external API calls.

## Configuration Files

The BitcoinInfo project uses YAML configuration files to handle different environment settings. These configuration files help in managing the application's behavior in development and production environments, as well as in managing the database and API connections.

### `config.dev.yaml`

This file contains the configuration for the **development environment**. It is intended for local usage where debugging is required. Here's a breakdown of the key sections:

```yaml
app:
  name: "BitcoinInfo"         # The name of the application
  version: "0.0.1"            # Version of the application
  debug: true                 # Enables debug mode for better error tracking in development
  port: 8080                  # The port where the application will be served locally

database:
  host: "localhost"           # Database host (local in development)
  port: 5432                  # Port on which the PostgreSQL database runs
  user: "postgres"            # Database user
  password: "postgres"        # Database password
  name: "bitcoininfo"         # Name of the database where data will be stored

api:
  endpoint: https://blockchain.info  # API endpoint for fetching blockchain data
  confirmations: 6                   # Minimum number of confirmations before a transaction is considered complete
  retry_attempts: 3                  # Number of retry attempts in case of failure
  timeout: 5                         # Timeout in seconds for API requests
```

- **app**: Contains basic settings for the application such as name, version, and whether to run in debug mode.
- **database**: Defines the connection to the PostgreSQL database, including host, port, username, password, and the database name.
- **api**: Defines the settings for the Blockchain API such as the endpoint, minimum confirmations, number of retries, and the timeout value.

### `config.prod.yaml`

This file is similar to the development configuration, but is tailored for the **production environment**. Here’s how it differs from the development config:

```yaml
app:
  name: "BitcoinInfo"
  version: "0.0.1"
  debug: true                  # In production, you may want to set this to `false`
  port: 8080                   # Port for the production environment

database:
  host: "postgres"             # Production database host (could be a remote DB server)
  port: 5432
  user: "postgres"
  password: "postgres"
  name: "bitcoininfo"

api:
  endpoint: https://blockchain.info
  confirmations: 6
  retry_attempts: 3
  timeout: 5
```

The production configuration file is almost identical to the development one, with the major difference being the **database host**, which would typically point to a production database server (e.g., a cloud-hosted PostgreSQL instance) instead of the local database used in development.

### Common Fields

- **app**: Holds the general information and settings of the application. The `debug` field should generally be set to `false` in production environments to avoid exposing sensitive error information.
- **database**: Contains the necessary credentials and connection details for PostgreSQL. In production, ensure that the password is secured and that the host points to your production database.
- **api**: The API configuration remains consistent across environments since it connects to the same blockchain API service. You may adjust the `timeout` or `retry_attempts` based on the network conditions of the production environment.

### How to Switch Between Configurations

The project is set up to use the appropriate configuration file based on the environment variable `APP_ENV`. In the `docker-compose.yaml`, you can see the environment being set as follows:

```yaml
flask_app:
  environment:
    - APP_ENV=prod           # Set this to "dev" for development environment
```

- If `APP_ENV` is set to `dev`, the application will load `config.dev.yaml`.
- If `APP_ENV` is set to `prod`, the application will load `config.prod.yaml`.

You can easily switch between the configurations by changing the value of this environment variable in your Docker Compose file or your system’s environment variables.

## License

This project is licensed under the Apache License 2.0. You can find the full license text in the [LICENSE](./LICENSE) file.

```
Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0
```
