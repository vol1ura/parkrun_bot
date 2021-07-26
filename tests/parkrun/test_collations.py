import os

from parkrun.collations import CollationMaker


def test_collation_maker_pics(athlete_data_1, athlete_data_2, tmpdir):
    bars_path = tmpdir.join('collation_bars.png')
    maker = CollationMaker(athlete_data_1.name, athlete_data_1.html, athlete_data_2.name, athlete_data_2.html)
    maker.bars(bars_path).close()
    assert os.path.exists(bars_path)

    scatter_path = tmpdir.join('collation_scatter.png')
    maker.scatter(scatter_path)
    assert os.path.exists(scatter_path)
    print('Files:', bars_path, scatter_path)


def test_collation_maker_table(athlete_data_1, athlete_data_2):
    maker = CollationMaker(athlete_data_1.name, athlete_data_1.html, athlete_data_2.name, athlete_data_2.html)
    table = maker.table()
    print(table)
    assert '*Всего совместных забегов*:' in table
    assert 'По разнице результатов вы' in table


def test_collation_maker_excel(athlete_data_1, athlete_data_2, tmpdir):
    xslx_path = tmpdir.join('collation.xlsx')
    maker = CollationMaker(athlete_data_1.name, athlete_data_1.html, athlete_data_2.name, athlete_data_2.html)
    maker.to_excel(xslx_path).close()
    assert os.path.exists(xslx_path)
    print('File:', xslx_path)
