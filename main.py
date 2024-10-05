# Description: Main entry point for the application
import os
from config import Config
from server import ServerApp

if __name__ == "__main__":
    config = Config(os.getenv("ENV", "dev"))
    serverApp = ServerApp(config)
    serverApp.run()
