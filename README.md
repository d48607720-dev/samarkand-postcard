# samarkand-postcard

Telegram-мини-апп: открытка для Альбины. Конверт, 10 общих вопросов, предупреждение,
10 личных, 5 вопросов куда пойти в Самарканде, календарь. Ответ приходит Давиду в личку.
Лимит: 2 прохождения. Доступ только у двух ID.

## Запуск
1. @BotFather: /newbot, скопируй токен.
2. GitHub: репозиторий `samarkand-postcard`, залей все файлы.
3. Railway: New Project, Deploy from GitHub repo.
4. Variables: `BOT_TOKEN`. Settings, Networking: Generate Domain.
   Если домен не подхватился сам, добавь `WEBAPP_URL`.
5. Давид и Альбина нажимают /start у бота.
6. Проверь сам: тест не тратит попытки, ответ придёт тебе.

## Переменные
- BOT_TOKEN (обязательно)
- WEBAPP_URL (если домен не подхватился)
- необязательно: OWNER_ID, GIRL_ID, MAX_USES

## Что менять
Места и кафе: `PARKS`, `CAFES`. Вопросы: `QUIZ1`, `QUIZ2`, `QUIZ3` в `public/index.html`.
