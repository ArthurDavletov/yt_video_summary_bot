# [yt_video_summary_bot](https://github.com/ArthurDavletov/yt_video_summary_bot)

Telegram-бот для получения пересказа с YouTube

## Настройка YandexGPT

1) Для работы нужно создать аккаунт на [Яндекс.Облаке](https://yandex.cloud/ru) и организацию (это не связано с юридическими сложностями 😁). 
Создать платёжный счёт, пополнить его (один запрос занимает примерно 3-10 рублей).
После создания организации вы можете достать переменную для `YANDEX_FOLDER_ID`: https://console.yandex.cloud/cloud/{YOUR_YANDEX_FOLDER_ID}
2) Создать сервисный аккаунт во вкладке _Identity and Access Management_. 
Он должен быть с ролью `ai.languageModels.user`
3) Создать API-ключ с областью действия `yc.ai.languageModels.execute`. Его можно записать в качестве `YANDEX_API_KEY`

## Запуск

Для запуска необходимо создать файл `.env` (в корневой директории) с токеном бота, API-ключом + папки из YandexGPT:

```text
TELEGRAM_TOKEN=12345:qwerty
YANDEX_API_KEY=Kaoru_Hana_wa_Rin_to_Saku
YANDEX_FOLDER_ID=Mahiru_Shiina
```

Далее запустить Docker:

```shell
sudo ./build.sh
```

## Логирование

Логи собираются в папку `./bot/modules/logs/`

Благодаря `RotatingFileHandler`, там может быть максимум 3 файла до 5 МБ каждый.

## Дальнейшее развитие

Если вы захотите улучшить, изменить код, то можете написать мне. :)