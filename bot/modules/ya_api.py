import asyncio
import os
import re

from yandex_cloud_ml_sdk import YCloudML
from yandex_cloud_ml_sdk.exceptions import AioRpcError

from bot.modules.logger import get_logger

logger = get_logger(__name__)

async def summarize_text(text: str) -> str:
    """Получение краткого содержания видеоролика с YouTube"""
    try:
        sdk = YCloudML(
            folder_id = os.getenv("YANDEX_FOLDER_ID"),
            auth = os.getenv("YANDEX_API_KEY"),
        )
    except Exception as e:
        logger.error(f"Недокументированная ошибка!", exc_info=e)
        raise e
    model = sdk.models.completions("yandexgpt")
    model = model.configure(temperature=0.5)
    try:
        result = model.run(
            [
                {"role": "system", "text": "Ты - полезный помощник, который создаёт краткие содержания видео с YouTube."},
                {"role": "user", "text": f"Пожалуйста, предоставь краткое изложение следующей расшифровки:\n\n{text}"},
            ]
        )
    except AioRpcError as e:
        logger.error(f"Ошибка во время запроса к YandexGPT. Текст ошибки:\n{e}")
        raise e
    except RuntimeError as e:
        if re.match(r"text length is \d+, which is outside the range", e.args[0]):
            logger.error(f"Длина запроса превышает лимит! {e}")
        else:
            logger.error(f"Ошибка во время выполнения: {e}")
        raise e
    except Exception as e:
        logger.error(f"Недокументированная ошибка!", exc_info=e)
        raise e
    summary = result[0].text
    return summary
