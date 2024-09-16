from dotenv import load_dotenv
from mock import MagicMock, Mock
import pytest

from ShareEz import ShareEz, ShareEzAuth


load_dotenv()


ShareEz_URL = "https://TEST_DOMAIN/api"
ShareEz_CLIENT_ID = "1234567890"
ShareEz_CLIENT_SECRET = "qwertyuiopasdfghjkl;'"  # nosec
ShareEz_TOKEN = "TOKEN"  # nosec


@pytest.fixture
def ShareEz_auth(requests_mock) -> ShareEzAuth:
    requests_mock.post(f"{ShareEz_URL}/oauth2/token", json={"access_token": ShareEz_TOKEN})
    return ShareEzAuth(
        url=ShareEz_URL, client_id=ShareEz_CLIENT_ID, client_secret=ShareEz_CLIENT_SECRET
    )


@pytest.fixture
def ShareEz() -> ShareEz:
    auth = MagicMock()
    auth.url = ShareEz_URL
    auth.fetch_token = Mock(return_value=ShareEz_TOKEN)
    return ShareEz(auth)
