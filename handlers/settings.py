from aiogram import types
from aiogram.dispatcher import FSMContext

import keyboards as kb

from app import dp


@dp.message_handler(commands='reset', state='*')
@dp.throttled(rate=1)
async def process_command_reset(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return
    await state.reset_state()
    kbd = await kb.main(message.from_user.id)
    await message.reply('Запрос отменён', reply_markup=kbd)
