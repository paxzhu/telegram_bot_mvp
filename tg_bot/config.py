import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN: str | None = os.getenv("BOT_TOKEN")
APIFY_TOKEN: str | None = os.getenv("APIFY_TOKEN")
GOOGLE_API_KEY: str | None = os.getenv("GOOGLE_API_KEY")
# STABILITY_API_KEY: str | None = os.getenv("STABILITY_API_KEY")
OPENAI_API_KEY: str | None = os.getenv("OPENAI_API_KEY")

for env_var, name in [
    (BOT_TOKEN, "BOT_TOKEN"),
    (APIFY_TOKEN, "APIFY_TOKEN"),
    (GOOGLE_API_KEY, "GOOGLE_API_KEY"),
    # (STABILITY_API_KEY, "STABILITY_API_KEY"),
    (OPENAI_API_KEY, "OPENAI_API_KEY"),
]:
    if env_var is None:
        raise RuntimeError(f"{name} 环境变量未设置！")