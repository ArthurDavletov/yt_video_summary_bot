import asyncio
import aiohttp
import yt_dlp
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound

from bot.modules.logger import get_logger

logger = get_logger(__name__)

class Video:
    """Класс, отвечающий за получение данных о видео"""
    def __init__(self, url: str) -> None:
        """Инициализатор объекта класса.

        :param url: Ссылка на видео
        """
        self.url: str = url
        self.id: str
        self.title: str
        self.extractor: str
        self.info: dict = {}
        self.views: int | None = None
        self.likes: int | None = None
        self.dislikes: int | None = None
        self.upload_date: str | None = None
        self.uploader: str | None = None
        self.duration: int
        self.__raw_formats: list[str, dict] | None = None
        self.formats: dict[str, dict[str, str]] | None = {}

    async def fetch_info(self):
        """Непосредственно парсит информацию, обновляя атрибуты объекта."""
        self.info = await asyncio.to_thread(yt_dlp.YoutubeDL().extract_info, self.url, download = False)
        self.__parse_info()
        await self.__update_dislikes()

    def get_likes_dislikes_text(self) -> str | None:
        """Возвращает строку с визуализацией лайков и дизлайков.

        :returns: Строка из 10 символов 👍 и 👎. None, если нет лайков или дизлайков"""
        if self.likes is None or self.dislikes is None:
            return None
        likes_count = int(self.likes / (self.dislikes + self.likes) * 10)
        dislikes_count = 10 - likes_count
        return "👍" * likes_count + "👎" * dislikes_count

    def get_time(self) -> str:
        """Возвращает время в формате MM:SS. Если видео длиннее часа, то в формате HH:MM:SS.

        :returns: Время в формате MM:SS или HH:MM:SS"""
        s = self.duration
        if s >= 3600:
            return f"{int(s / 3600):0>2}:{int(s % 3600) // 60:0>2}:{int(s % 60):0>2}"
        return f"{int(s // 60):0>2}:{int(s % 60):0>2}"

    def __parse_info(self):
        """Отвечает за обновление атрибутов."""
        if not self.info:
            return
        self.url = self.info.get("webpage_url", self.url)
        self.id = self.info.get("id")
        self.title = self.info.get("title")
        self.duration = self.info.get("duration")
        self.description = self.info.get("description")
        self.views = self.info.get("view_count")
        self.likes = self.info.get("like_count")
        self.dislikes = self.info.get("dislike_count")
        self.upload_date = self.info.get("upload_date")
        self.__raw_formats = self.info.get("formats")
        if self.upload_date is not None:
            year, month, day = self.upload_date[:4], self.upload_date[4:6], self.upload_date[6:]
            self.upload_date = f"{day}.{month}.{year}"
        self.uploader = self.info.get("uploader")
        self.extractor = self.info.get("extractor")

    async def __update_dislikes(self):
        """Обновляет количество дизлайков у YouTube"""
        if self.extractor != "youtube":
            return
        url = f"https://returnyoutubedislikeapi.com/votes?videoId={self.id}"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    self.dislikes = data.get("dislikes")


async def fetch_transcript(video_id: str) -> str:
    languages: list[str] = ["ru", "en"]
    """Извлечение текста видео с YouTube"""
    try:
        transcript_list = YouTubeTranscriptApi().fetch(video_id, languages = languages)
        text = " ".join(snippet.text for snippet in transcript_list.snippets)
        return text
    except TranscriptsDisabled as e:
        logger.error(f"Расшифровка для видео отключена: https://youtu.be/{video_id}/")
        raise e
    except NoTranscriptFound as e:
        logger.error(f"Не найдено расшифровок для языков {languages} для видео: https://youtu.be/{video_id}/")
        raise e
    except Exception as e:
        logger.error(f"Произошла недокументированная ошибка во время извлечения расшифровки: "
                     f"https://youtu.be/{video_id}/.", exc_info=e)
        raise e
