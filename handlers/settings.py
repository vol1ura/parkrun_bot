from aiogram import types
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext

import keyboards as kb

from app import dp, language_code
from utils.content import t


@dp.message(Command('reset'), StateFilter('*'))
async def process_command_reset(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state:
        await state.clear()
    await message.reply(t(language_code(message), 'request_cancelled'), reply_markup=await kb.main(message))
