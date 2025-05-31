import qrcode
import os

from contextlib import contextmanager
from qrcode.image.pure import PyPNGImage


@contextmanager
def generate(athlete_code: int):
    code_obj = qrcode.make(f'A{athlete_code}', image_factory=PyPNGImage, box_size=8, border=3)
    qrcode_file = f'gen_png/qrcode_{athlete_code}.png'
    code_obj.save(qrcode_file)
    file_obj = open(qrcode_file, 'rb')
    yield file_obj
    if file_obj:
        file_obj.close()
    if os.path.exists(qrcode_file):
        os.remove(qrcode_file)
