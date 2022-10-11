from aiogram import types
from aiogram.dispatcher import FSMContext

import keyboards as kb
from app import bot, dp, db_conn
from handlers.helpers import UserStates
from utils import content, redis


@dp.message_handler(commands='reset', state='*')
@dp.throttled(rate=1)
async def process_command_reset(message: types.Message, state: FSMContext):
	current_state = await state.get_state()
	if current_state is None:
		return
	await state.reset_state()
	await message.reply('Запрос отменён')


@dp.callback_query_handler(lambda c: c.data == 'athlete_code_search')
@dp.throttled(rate=5)
async def process_athlete_code_search(callback_query: types.CallbackQuery):
	await bot.answer_callback_query(callback_query.id)
	await UserStates.SEARCH_ATHLETE_CODE.set()
	await bot.delete_message(callback_query.message.chat.id, callback_query.message.message_id)
	await bot.send_message(callback_query.from_user.id, content.athlete_code_search, parse_mode='Markdown')
