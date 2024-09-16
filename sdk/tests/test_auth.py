import json

from mock import Mock
import pytest

from ShareEz import ShareEzAuth
from ShareEz.exceptions import AuthenticationErrorException, CannotFindCredentialException


class MockRequestResponse:
    def __init__(self, status_code: int = 200, content=None):
        self.status_code = status_code
        self.content = content


class TestAuth:
    def test_evaluate_inputs_with_value(self, ShareEz_auth: ShareEzAuth):
        value = "value"
        result = ShareEz_auth.evaluate_inputs(value, "ENVIRONMENT_VARIABLE")
        assert result == value

    def test_evaluate_inputs_without_either_value(self, ShareEz_auth: ShareEzAuth):
        with pytest.raises(CannotFindCredentialException):
            ShareEz_auth.evaluate_inputs(None, "ENVIRONMENT_VARIABLE")

    def test_evaluate_inputs_with_environment_variable(
        self, ShareEz_auth: ShareEzAuth, monkeypatch
    ):
        name = "ENVIRONMENT_VARIABLE"
        value = "value"
        monkeypatch.setenv(name, value)
        result = ShareEz_auth.evaluate_inputs(None, name)
        assert result == value

    def test_validate_credentials_success(self, ShareEz_auth: ShareEzAuth):
        ShareEz_auth.request_token = Mock(return_value=MockRequestResponse(200))
        ShareEz_auth.validate_credentials()
        ShareEz_auth.request_token.assert_called_once()

    def test_validate_credentials_failure(self, ShareEz_auth: ShareEzAuth):
        ShareEz_auth.request_token = Mock(return_value=MockRequestResponse(401))
        with pytest.raises(AuthenticationErrorException):
            ShareEz_auth.validate_credentials()
            ShareEz_auth.request_token.assert_called_once()

    def test_fetch_token(self, ShareEz_auth: ShareEzAuth):
        mocked_response = MockRequestResponse(
            content=json.dumps({"access_token": "token"}).encode("utf-8")
        )
        ShareEz_auth.request_token = Mock(return_value=mocked_response)
        res = ShareEz_auth.fetch_token()
        assert res == "token"
