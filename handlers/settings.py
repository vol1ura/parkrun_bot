from aiogram import types
from aiogram.dispatcher import FSMContext

import keyboards as kb

from app import dp, language_code
from utils import content


# @dp.throttled(rate=1)
@dp.message_handler(commands='reset', state='*')
async def process_command_reset(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return
    await state.reset_state()
    kbd = await kb.main(message)
    await message.reply(content.t(language_code(message), 'request_cancelled'), reply_markup=kbd)
