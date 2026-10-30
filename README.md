# Telegram User Info Bot (Render)

This bot replies to `/start` with the Telegram profile details that the Bot API makes available for the person who starts it.

## Information shown
- First and last name (when provided)
- Username (if set)
- Telegram user ID
- Premium status (if Telegram reports it)
- Language code (if provided)
- Profile photo (if the user has one and the API allows it)

## Important limitation
Telegram's Bot API does **not** provide account creation date, phone number, email, IP address, or a complete/private account profile. The bot clearly labels the creation date as unavailable; it does not guess it.

## Deploy on Render
1. Create a Telegram bot with `@BotFather` and copy its bot token.
2. Upload this project to a GitHub repository.
3. In Render, choose **New + → Blueprint** and connect that repository. Render reads `render.yaml`.
4. In the Render service's Environment settings, add `BOT_TOKEN` and paste your token.
5. Deploy. Open your bot in Telegram and send `/start`.

This project runs as a background worker using long polling, so it does not need a web server or a public webhook URL.

## Keep your token private
Never publish your bot token in source code, screenshots, or public repositories. If a token leaks, revoke it with `@BotFather` and create a new one.
