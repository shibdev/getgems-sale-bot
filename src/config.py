from environs import Env

env = Env()
env.read_env(".env")


BOT_TOKEN = env.str("BOT_TOKEN")
CONNECT_URL = env.str("CONNECT_URL")
