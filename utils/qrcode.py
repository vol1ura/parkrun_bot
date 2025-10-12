import qrcode
import os

from contextlib import contextmanager
from qrcode.image.pure import PyPNGImage
from aiogram.types import BufferedInputFile


@contextmanager
def generate(athlete_code: int):
    code_obj = qrcode.make(f'A{athlete_code}', image_factory=PyPNGImage, box_size=8, border=3)
    qrcode_file = f'gen_png/qrcode_{athlete_code}.png'
    code_obj.save(qrcode_file)

    with open(qrcode_file, 'rb') as f:
        file_content = f.read()

    buffered_file = BufferedInputFile(file_content, filename=f'qrcode_{athlete_code}.png')

    try:
        yield buffered_file
    finally:
        if os.path.exists(qrcode_file):
            os.remove(qrcode_file)
