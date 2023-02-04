from contextlib import contextmanager
import barcode
import os


@contextmanager
def generate(athlete_code: int):
    code128 = barcode.get_barcode_class('code128')
    code_obj = code128(f'A{athlete_code}', writer=barcode.writer.ImageWriter())
    barcode_file = code_obj.save(f'gen_png/barcode_{athlete_code}')
    file_obj = open(barcode_file, 'rb')
    yield file_obj
    if file_obj:
        file_obj.close()
        os.remove(barcode_file)
