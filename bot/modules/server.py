import asyncio
import logging
import os
import re

from aiogram import Bot, Dispatcher, types, F
from aiogram.filters.command import CommandStart
from aiogram.utils.formatting import Text, ExpandableBlockQuote, Code
from aiogram.types import LinkPreviewOptions

from youtube_transcript_api import CouldNotRetrieveTranscript
from dotenv import load_dotenv
from bot.modules.yt_api import Video, fetch_transcript
from bot.modules.ya_api import summarize_text
from bot.modules.logger import get_logger

load_dotenv()
logger = get_logger(__name__)

dp = Dispatcher()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
if not TELEGRAM_TOKEN:
    logger.error("TELEGRAM_TOKEN не указан.")
    raise ValueError("Пожалуйста, укажите TELEGRAM_TOKEN в файле .env")
bot = Bot(token = TELEGRAM_TOKEN)
del TELEGRAM_TOKEN

YOUTUBE_URL_REGEX = re.compile(
    r'(?:https?://)?(?:www.)?(?:youtube\.com/watch\?v=|youtu\.be/)([A-Za-z0-9_-]+)'
)

@dp.message(CommandStart())
async def cmd_start(message: types.Message):
    await message.reply(
        "Привет! Отправь мне ссылку на YouTube, и я отвечу вам кратким содержанием видео.",
    )


def find_urls(message: types.Message) -> list[str]:
    """Находит ссылки в сообщении.

    :param message: Сообщение пользователя.
    :returns: Список ссылок.
    """
    urls = []
    if not message.entities:
        return urls
    for entity in message.entities:
        if entity.type == "url":
            urls.append(entity.extract_from(message.text))
        elif entity.type == "text_link":
            urls.append(entity.url)
    return urls

def content_generator(video: Video) -> Text:
    """Генерирует содержимое сообщения.

    :param video: Объект видео с заполненным полями.
    :returns: Сообщение с краткой информацией.
    """
    content = Text(
        video.title,
        "\n🕒 ", Code(video.get_time()),
    )
    # Сообщение формируется последовательно. Если середина не пуста (None),
    # то слева и справа от собственной информации добавляются фрагменты. Стоит отметить, что каждый фрагмент
    # начинается с новой строки (кроме дизлайков), а заканчивается не пустой. Без лайков не будет и дизлайков
    words = (
        ("\n👀 ", video.views, ""), (" | 👍 ", video.likes, ""), (" : ", video.dislikes, " 👎"),
        ("\n📤 ", video.upload_date, ""),
        ("\n👤 ", video.uploader, ""),
        ("\n", video.get_likes_dislikes_text(), ""),
        ("\nОписание: ", ExpandableBlockQuote(video.description) if video.description else None, "")
    )
    for pre, body, post in words:
        if body is not None:
            content += Text(pre, body, post)
    return content

@dp.message(F.text)
async def cmd_text(message: types.Message):
    urls = find_urls(message)
    if not urls:
        await message.reply("В сообщении не нашлось ссылок на видео :(")
        return
    if len(urls) > 1:
        await message.reply(f"Количество ссылок: {len(urls)}. "
                            f"Но пока я не умею работать с несколькими ссылками :(")
        return
    url = urls[0]
    small_link_options = LinkPreviewOptions(
        url = url,
        prefer_small_media = True
    )
    answer = await message.reply(f"Я нашёл ссылку: {urls[0]}.\nПодождите немного...",
                                 link_preview_options = small_link_options)
    video = Video(url)
    await video.fetch_info()
    await answer.edit_text(**content_generator(video).as_kwargs(),
                           link_preview_options = small_link_options)
    match = YOUTUBE_URL_REGEX.search(url)
    if not match:
        await message.reply("⚠️ Не удалось обнаружить правильный URL-адрес YouTube. Пожалуйста, попробуйте снова.")
        return
    video_id = match.group(1)
    m = await message.reply("🔍 Получение расшифровки...")
    try:
        transcript = await fetch_transcript(video_id)
    except CouldNotRetrieveTranscript as e:
        await m.edit_text(f"❌ Произошла ошибка во время получения расшифровки")
        return
    await m.edit_text("🧠 Создание краткого содержания с помощью YandexGPT...")
    try:
        summary = await summarize_text(transcript)
    except Exception as e:
        if re.match(r"text length is \d+, which is outside the range", e.args[0]):
            await m.edit_text("❌ Длина текста превышает лимит :(")
        else:
            await m.edit_text("❌ Произошла ошибка при работе с YandexGPT.")
        return
    try:
        await m.edit_text(f"📝 Содержание:\n\n{summary}")
    except Exception as e:
        logger.error(f"Неизвестная ошибка при отправке сообщения!", exc_info=e)
        raise e


async def main():
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())