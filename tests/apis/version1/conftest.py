import pathlib
import pytest

from tests import TEST_DATA_DIR


@pytest.fixture
def raman_soddyite_rruff_file():
    """
    Raman RRUFF file for Soddyite for wavelength 780 nm
    Retrieved on 1/12/2021 from:
        https://rruff.info/tmp_rruff/Soddyite__R060361__Broad_Scan__780__0__unoriented__Raman_Data_RAW__21504.rruff  # noqa: E501
    """
    p = pathlib.Path(TEST_DATA_DIR, "rruff", "raman_soddyite.rruff")
    return p


@pytest.fixture
def raman_soddyite_jcamp_file():
    """
    Raman RRUFF file for Soddyite for wavelength 780 nm (in JCAMP format)
    Retrieved RRUFF file on 1/12/2021 from:
        https://rruff.info/tmp_rruff/Soddyite__R060361__Broad_Scan__780__0__unoriented__Raman_Data_RAW__21504.rruff  # noqa: E501
    """
    p = pathlib.Path(TEST_DATA_DIR, "jcamp", "raman_soddyite.jdx")
    return p


@pytest.fixture
def raman_soddyite_scidata_jsonld_file():
    """
    SciData JSON-LD conversion of Soddyite RRUFF file above using SciDataLib
    """
    p = pathlib.Path(TEST_DATA_DIR, "scidata-jsonld", "raman_soddyite.jsonld")
    return p


@pytest.fixture
def raman_soddyite_ssm_json_file():
    """
    SSM abbreviated JSON conversion of Soddyite RRUFF file above
    """
    p = pathlib.Path(TEST_DATA_DIR, "ssm-json", "raman_soddyite.json")
    return p
