import rollbar

from aiogram.utils.exceptions import TelegramAPIError, BotBlocked, InvalidQueryID

from app import dp, logger, bot
from bot_exceptions import ParsingException, CallbackException, NoCollationRuns
from config import ROLLBAR_TOKEN, PRODUCTION_ENV


rollbar.init(ROLLBAR_TOKEN, 'production' if PRODUCTION_ENV else 'development')


@dp.errors_handler(exception=ParsingException)
async def parsing_errors_handler(update, error):
    """
    We collect some info about an exception and write to log
    """
    error_msg = f"Exception of type {type(error)}. Chat ID: {update.message.chat.id}. " \
                f"User ID: {update.message.from_user.id}. Error: {error}"
    await bot.send_message(update.message.chat.id, 'Не могу получить эти данные.\n'
                                                   'Скорее всего, их пока просто нет 😿\n'
                                                   'Попробуйте выбрать другой паркран или клуб.')
    logger.error(error_msg)
    return True


@dp.errors_handler(exception=CallbackException)
async def callback_errors_handler(update, error):
    error_msg = f"Exception of type {type(error)}. UserName: {update.callback_query.from_user.username}. " \
                f"User ID: {update.callback_query.from_user.id}. Error: {error}"
    await bot.send_message(update.callback_query.from_user.id, error)
    logger.error(error_msg)
    notify_in_rollbar(error)
    return True


@dp.errors_handler(exception=NoCollationRuns)
async def no_collation_runs_handler(update, error):
    error_msg = f"Exception {type(error)}. UserName: {update.callback_query.from_user.username}. " \
                f"User ID: {update.callback_query.from_user.id}. Error: no collation runs with {error}"
    await bot.send_message(update.callback_query.from_user.id, f'У вас пока ещё не было совместных пробежек с {error}')
    logger.error(error_msg)
    return True


@dp.errors_handler(exception=InvalidQueryID)
async def invalid_query_id_handler(update, error):
    message = 'Извините, запуск бота занял много времени. Теперь бот готов отвечать. Повторите запрос.'
    if update.callback_query:
        await bot.send_message(update.callback_query.from_user.id, message)
        logger.error(f"Callback data: {update.callback_query}")
    elif update.message:
        await bot.send_message(update.message.chat.id, message)
    else:
        logger.warning(f'{update} update object was not processed')
    logger.error(f"InvalidQueryID error. Update type: {type(update)}, Error: {error}")
    notify_in_rollbar(error)
    return True


@dp.errors_handler(exception=TelegramAPIError)
async def api_errors_handler(update, error):
    # Here we collect all available exceptions from Telegram and write them to log
    # First, we don't want to log BotBlocked exception, so we skip it
    if isinstance(error, BotBlocked):
        return True
    # We collect some info about an exception and write to log
    error_msg = f"Exception {type(error)}. Error: {error}"
    logger.error(error_msg)
    notify_in_rollbar(error)
    return True


@dp.errors_handler(exception=Exception)
async def general_exeption_handler(update, error):
    error_msg = f"Exception {type(error)}. Error: {error}"
    logger.error(error_msg)
    notify_in_rollbar(error)
    return True


def notify_in_rollbar(error):
    rollbar.report_exc_info((type(error), error, error.__traceback__))
