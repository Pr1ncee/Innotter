import dotenv

config = dotenv.dotenv_values(".env")

# JWT
JWT_SECRET_KEY = config["JWT_SECRET_KEY"]
JWT_SIGNING_METHOD = config["JWT_SIGNING_METHOD"]

# RabbitMQ 
RABBITMQ_USERNAME = config["RABBITMQ_DEFAULT_USER"]
RABBITMQ_PASSWORD = config["RABBITMQ_DEFAULT_PASS"]
RABBITMQ_HOST = config["RABBITMQ_HOST"]
RABBITMQ_PORT = config["RABBITMQ_PORT"]
RABBITMQ_HEARTBEAT, RABBITMQ_TIMEOUT = 600, 300
RABBITMQ_EXCHANGE = config["RABBITMQ_EXCHANGE_NAME"]

# AWS
AWS_REGION_NAME = config["AWS_REGION_NAME"]
AWS_ACCESS_KEY_ID = config["AWS_ACCESS_KEY_ID"]
AWS_SECRET_ACCESS_KEY = config["AWS_SECRET_ACCESS_KEY"]
PK = 'id'  # Primary key of the db's tables
ROUTING_KEY = 'stats'
USERS_NAME_TABLE, PAGES_NAME_TABLE, POSTS_NAME_TABLE = 'users', 'pages', 'posts'
