import rollbar

from aiogram.exceptions import TelegramBadRequest
from aiogram.types import ErrorEvent

from app import dp, logger, bot
from bot_exceptions import ParsingException, CallbackException, NoCollationRuns
from config import ROLLBAR_TOKEN, PRODUCTION_ENV


rollbar.init(ROLLBAR_TOKEN, 'production' if PRODUCTION_ENV else 'development')


@dp.error()
async def error_handler(event: ErrorEvent):
    """
    Global error handler for all exceptions
    """
    update = event.update
    exception = event.exception

    # Handle ParsingException
    if isinstance(exception, ParsingException):
        if update.message:
            error_msg = f"Exception of type {type(exception)}. Chat ID: {update.message.chat.id}. " \
                        f"User ID: {update.message.from_user.id}. Error: {exception}"
            await bot.send_message(update.message.chat.id, 'Не могу получить эти данные.\n'
                                                           'Скорее всего, их пока просто нет 😿\n'
                                                           'Попробуйте выбрать другой паркран или клуб.')
            logger.error(error_msg)
        return True

    # Handle CallbackException
    if isinstance(exception, CallbackException):
        if update.callback_query:
            error_msg = f"Exception of type {type(exception)}. UserName: {update.callback_query.from_user.username}. " \
                        f"User ID: {update.callback_query.from_user.id}. Error: {exception}"
            await bot.send_message(update.callback_query.from_user.id, str(exception))
            logger.error(error_msg)
            notify_in_rollbar(exception)
        return True

    # Handle NoCollationRuns
    if isinstance(exception, NoCollationRuns):
        if update.callback_query:
            error_msg = f"Exception {type(exception)}. UserName: {update.callback_query.from_user.username}. " \
                        f"User ID: {update.callback_query.from_user.id}. Error: no collation runs with {exception}"
            await bot.send_message(
                update.callback_query.from_user.id,
                f'У вас пока ещё не было совместных пробежек с {exception}'
            )
            logger.error(error_msg)
        return True

    # Handle TelegramBadRequest (InvalidQueryID and others)
    if isinstance(exception, TelegramBadRequest):
        # Check if it's an InvalidQueryID error
        if 'query is too old' in str(exception).lower() or 'query_id_invalid' in str(exception).lower():
            message = 'Извините, запуск бота занял много времени. Теперь бот готов отвечать. Повторите запрос.'
            if update.callback_query:
                await bot.send_message(update.callback_query.from_user.id, message)
                logger.error(f"Callback data: {update.callback_query}")
            elif update.message:
                await bot.send_message(update.message.chat.id, message)
            else:
                logger.warning(f'{update} update object was not processed')
            logger.error(f"InvalidQueryID error. Update type: {type(update)}, Error: {exception}")
            notify_in_rollbar(exception)
            return True

        # Handle other TelegramBadRequest errors (like BotBlocked)
        if 'bot was blocked by the user' in str(exception).lower():
            # Don't log BotBlocked exceptions
            return True

        # Log other TelegramBadRequest errors
        error_msg = f"Exception {type(exception)}. Error: {exception}"
        logger.error(error_msg)
        notify_in_rollbar(exception)
        return True

    # Handle all other exceptions
    error_msg = f"Exception {type(exception)}. Error: {exception}"
    logger.error(error_msg)
    notify_in_rollbar(exception)
    return True


def notify_in_rollbar(error):
    rollbar.report_exc_info((type(error), error, error.__traceback__))
