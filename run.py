import os
import django
from loguru import logger


@logger.catch
def main() -> None:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.local')
    django.setup()

    from scripts.trades import trade_loop
    trade_loop()


if __name__ == "__main__":
    main()
