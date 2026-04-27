import logging
from telegram.ext import Application
from .config import load_settings
from .storage import build_storage
from .handlers import build_handlers

logging.basicConfig(
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    level=logging.INFO,
)

def main() -> None:
    settings = load_settings()
    app = Application.builder().token(settings.bot_token).build()
    app.bot_data["settings"] = settings
    app.bot_data["storage"] = build_storage(settings)

    for handler in build_handlers():
        app.add_handler(handler)

    logging.info("Coach bot v0.2 started in polling mode.")
    app.run_polling(allowed_updates=None)

if __name__ == "__main__":
    main()
