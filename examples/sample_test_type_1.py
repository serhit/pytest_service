import pytest
import pandas

SHEET_NAME = 'Config'
TABLE_OFFSET = 0
KEY_FIELD = 'Code'


def get_config_data():
    data = pandas.read_excel("example_type_1.xlsx",
                             sheet_name=SHEET_NAME,
                             skiprows=TABLE_OFFSET)
    return data


# Generate array of rows - to parametrize tests
try:
    config_data_records = [rec for rec in get_config_data().iterrows() if str(rec[1][KEY_FIELD]) != 'nan']
    config_indexes = [rec[0] for rec in config_data_records]
except:
    config_data_records = None
    config_indexes = None


@pytest.fixture()
def config_dataset():
    return get_config_data()


@pytest.fixture(params=config_data_records, ids=config_indexes)
def config_record(request):
    return request.param[1], request.param[0] + TABLE_OFFSET + 2  # Excel rows start with 1, plus caption, plus offset


@pytest.mark.tryfirst
def test_data_exists():
    get_config_data()


# Test applies for whole rowset
@pytest.mark.parametrize("column_name", [KEY_FIELD, 'TextData', 'Numbers'])
def test_data_has_column(config_dataset, column_name):
    assert column_name in config_dataset.columns


# Test applies for each row of the file
@pytest.mark.parametrize("column_name", [KEY_FIELD, 'TextData'])
def test_mandatory_value_is_missing(config_record, column_name):
    rec, line_no = config_record
    assert not any(rec[[column_name]].isna())