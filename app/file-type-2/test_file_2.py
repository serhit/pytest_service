
import pytest
import pandas


SHEET_NAME = 'Data'
TABLE_OFFSET = 0
KEY_FIELD = 'ID'


def get_config_data():
    data = pandas.read_excel(pytest.data_file_name,
                             sheet_name=SHEET_NAME,
                             skiprows=TABLE_OFFSET,
                             dtype=str)

    # Here you may do any filtering of the records to be validated

    return data


# Generate array of rows - to parametrize tests
try:
    config_data_records = [rec for rec in get_config_data().iterrows() if str(rec[1][KEY_FIELD]) != 'nan']
    config_indexes = [rec[0] for rec in config_data_records]
except:
    config_data_records = None
    config_indexes = None


# Fixture for the set-based testing of the rules
@pytest.fixture()
def config_dataset():
    return get_config_data()


# Fixture for the row-based testing of the rules
@pytest.fixture(params=config_data_records, ids=config_indexes)
def config_record(request):
    return request.param[1], request.param[0] + TABLE_OFFSET + 2  # Excel rows start with 1, plus caption


#
# Test rules
#

@pytest.mark.tryfirst
@pytest.mark.dependency()
def test_data_exists(record_property):
    record_property("ref", SHEET_NAME)
    get_config_data()


expected_columns = [KEY_FIELD, 'Value']


@pytest.mark.parametrize("column_name", expected_columns)
@pytest.mark.dependency(depends=["test_data_exists"])
def test_data_has_column(config_dataset, column_name, record_property):
    record_property("field_name", column_name)
    assert column_name in config_dataset.columns
