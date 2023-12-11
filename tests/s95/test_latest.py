# import asyncio
# import random
# import re
# from datetime import datetime
# import os

# import pandas
# import pytest

# from bot_exceptions import ParsingException
# from s95 import latest
# from s95.helpers import ParkrunSite

PARKRUN = 'kuzminki'


# @pytest.fixture(scope='module')
# def yoshka_latest_results():
#     return asyncio.run(latest.parse_latest_results(PARKRUN))


# @pytest.fixture
# async def mock_yoshka_results(monkeypatch, yoshka_latest_results):
#     future = asyncio.Future()
#     future.set_result(yoshka_latest_results)
#     monkeypatch.setattr('parkrun.latest.parse_latest_results', lambda *args: future)


# def test_parse_latest_results(yoshka_latest_results):
#     df, parkrun_date = yoshka_latest_results
#     assert isinstance(df, pandas.DataFrame)
#     assert isinstance(parkrun_date, str)
#     assert isinstance(datetime.strptime(parkrun_date, '%d/%m/%Y'), datetime)


# async def test_parse_latest_results_fail(empty_page, monkeypatch):
#     future = asyncio.Future()
#     future.set_result(empty_page)
#     monkeypatch.setattr(ParkrunSite, 'get_html', lambda *args: future)
#     with pytest.raises(ParsingException) as e:
#         await latest.parse_latest_results('no_such_parkrun')
#     assert 'no_such_parkrun' in e.value.message


# async def test_make_latest_results_diagram(mock_yoshka_results, tmpdir):
#     pic_path = tmpdir.join('latest_diag.png')
#     pic_file = await latest.make_latest_results_diagram(PARKRUN, pic_path)
#     pic_file.close()
#     print(pic_path)
#     assert os.path.exists(pic_path)


# async def test_make_latest_results_diagram_personal(mock_yoshka_results, yoshka_latest_results, tmpdir):
#     pic_path = tmpdir.join('latest_diag_personal.png')
#     # Prepare athlete name for test
#     df, _ = yoshka_latest_results
#     df.dropna(thresh=3, inplace=True)
#     df.reset_index(inplace=True)
#     random_name = random.choice(df['Участник'].apply(lambda s: re.search(r'^([^\d]+)\d.*', s)[1]))
#     print(random_name)
#     # Build diagram with athlete name
#     pic_file = await latest.make_latest_results_diagram(
#         PARKRUN, pic_path, random_name.split()[-1], random.randrange(800)
#     )
#     pic_file.close()
#     print(pic_path)
#     assert os.path.exists(pic_path)


# async def test_make_latest_results_diagram_noperson(mock_yoshka_results, tmpdir):
#     pic_path = tmpdir.join('latest_diag_noperson.png')
#     with pytest.raises(AttributeError):
#         await latest.make_latest_results_diagram(PARKRUN, pic_path, 'no_such_name_athelete', random.randrange(800))


# async def test_make_clubs_bar(mock_yoshka_results, tmpdir):
#     pic_path = tmpdir.join('latest_clubs.png')
#     pic_file = await latest.make_clubs_bar(PARKRUN, pic_path)
#     pic_file.close()
#     print(pic_path)
#     assert os.path.exists(pic_path)


# async def test_review_table(mock_yoshka_results):
#     table = await latest.review_table(PARKRUN)
#     print(table)
#     assert isinstance(table, str)
#     assert f'*Паркран {PARKRUN}* состоялся' in table


# async def test_review_table_empty(monkeypatch, yoshka_latest_results):
#     future = asyncio.Future()
#     future.set_result((yoshka_latest_results[0][0:0], yoshka_latest_results[1]))
#     monkeypatch.setattr('parkrun.latest.parse_latest_results', lambda *args: future)
#     message = await latest.review_table(PARKRUN)
#     assert isinstance(message, str)
#     assert message == f'Паркран {PARKRUN} {yoshka_latest_results[1]} не состоялся.'
