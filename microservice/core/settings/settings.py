import dotenv

config = dotenv.dotenv_values(".env")

# JWT
JWT_SECRET_KEY = config["JWT_SECRET_KEY"]
SIGNING_METHOD = config["SIGNING_METHOD"]

# RabbitMQ 
USERNAME = config["RABBITMQ_DEFAULT_USER"]
PASSWORD = config["RABBITMQ_DEFAULT_PASS"]
HOST = config["RABBITMQ_HOST"]
PORT = config["RABBITMQ_PORT"]
HEARTBEAT, TIMEOUT = 600, 300
EXCHANGE = config["RABBITMQ_EXCHANGE_NAME"]

# AWS
REGION_NAME = config["AWS_REGION_NAME"]
AWS_ACCESS_KEY_ID = config["AWS_ACCESS_KEY_ID"]
AWS_SECRET_ACCESS_KEY = config["AWS_SECRET_ACCESS_KEY"]
PK = 'id'  # Primary key of the db's tables
ROUTING_KEY = 'stats'
TABLE_NAME_USERS = 'users'
