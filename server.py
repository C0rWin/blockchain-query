import os
import traceback

from config import Config
from bitcoin_info import AddressService as address_service
from bitcoin_info import TransactionService as transaction_service
from db.database import CacheManager

from flask import Flask, request, jsonify, g
from flask_cors import CORS
from flask.views import MethodView
from flask_limiter import Limiter
from time import strftime


class ServerApp:
    """
    ServerApp class, which is responsible for running the Flask application.
    It initializes the Flask application and registers the routes.

    The available routes are:

    - /address/<address> -> GET (returns the balance and transaction count for the given address)
    - /transaction/<txhash> -> GET (returns the transaction details for the given transaction hash)
    """

    def __init__(self, config: Config):
        """
        Initialize the ServerApp with the given configuration.

        Parameters:
        - config (Config): The configuration object.
        """
        self._config = config
        self._app = Flask(config["app"]["name"])
        self._limiter = Limiter(app=self._app, key_func=lambda: request.remote_addr)

        db_uri = f"postgresql://{config['database']['user']}:{config['database']['password']}@{config['database']['host']}:{config['database']['port']}/{config['database']['name']}"
        self._cache = CacheManager(db_uri)
        self._register_routes()
        self._register_error_handlers()

    def _log_request(self):
        self._app.logger.info(
            f'{request.remote_addr} - - [{strftime("%d/%b/%Y %H:%M:%S")}] '
            f'"{request.method} {request.full_path} {request.scheme.upper()}" '
            f"{request.user_agent}"
        )

    def _register_routes(self):
        @self._app.before_request
        def before_request():
            g.start = strftime("[%d/%b/%Y %H:%M:%S]")
            self._log_request()

        @self._app.after_request
        def after_request(response):
            diff = strftime("[%d/%b/%Y %H:%M:%S]")
            self._app.logger.info(
                f"{g.start} {diff} {request.remote_addr} {request.method} "
                f"{request.full_path} {response.status}"
            )
            return response

        """
        Register the routes for the Flask application.
        """
        addressView = address_service.as_view(
            "address", self._config, self._cache, self._limiter
        )
        self._app.add_url_rule(
            "/address/<string:address>", view_func=addressView, methods=["GET"]
        )

        transactionView = transaction_service.as_view(
            "transaction", self._config, self._cache, self._limiter
        )
        self._app.add_url_rule(
            "/transaction/<string:txhash>",
            view_func=transactionView,
            methods=["GET"],
        )

    def _register_error_handlers(self):
        """
        Register the error handlers for the Flask application.
        """

        def error_response(error, status_code):
            response = jsonify(
                {
                    "error": type(error).__name__,
                    "message": str(error),
                    "status_code": status_code,
                    "url": request.url,
                    "method": request.method,
                    "path": request.path,
                    "remote_addr": request.remote_addr,
                }
            )
            response.status_code = status_code
            return response

        @self._app.errorhandler(400)
        def bad_request(e):
            return error_response(e, 400)

        @self._app.errorhandler(404)
        def not_found(e):
            return error_response(e, 404)

        @self._app.errorhandler(500)
        def internal_server_error(e):
            error_details = {
                "error": "Internal Server Error",
                "message": str(e),
                "status_code": 500,
                "url": request.url,
                "method": request.method,
                "path": request.path,
                "remote_addr": request.remote_addr,
            }
            if self._app.debug:
                error_details["traceback"] = traceback.format_exc()
            return jsonify(error_details), 500

        # Optionally, add a catch-all error handler
        @self._app.errorhandler(Exception)
        def handle_exception(e):
            return error_response(e, 500)

    def run(self):
        """
        Run the Flask application.
        """

        print(f"Application name: {self._config['app']['name']}")
        print(f"Running on port: {self._config['app']['port']}")
        print(f"Using API Endpoint: {self._config['api']['endpoint']}")
        CORS(self._app, resources={r"/*": {"origins": "*"}})
        for rule in self._app.url_map.iter_rules():
            methods = ",".join(rule.methods)
            line = f"{rule.endpoint:30s} -> {methods:20s} {rule}"
            print(line)
        self._app.run(
            port=self._config["app"]["port"],
            host="0.0.0.0",
            debug=self._config["app"]["debug"],
        )
