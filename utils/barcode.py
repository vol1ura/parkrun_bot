import qrcode
import os

from contextlib import contextmanager
from qrcode.image.pure import PyPNGImage


@contextmanager
def generate(athlete_code: int):
    code_obj = qrcode.make(f'A{athlete_code}', image_factory=PyPNGImage)
    barcode_file = f'gen_png/barcode_{athlete_code}'
    code_obj.save(barcode_file)
    file_obj = open(barcode_file, 'rb')
    yield file_obj
    if file_obj:
        file_obj.close()
        os.remove(barcode_file)
