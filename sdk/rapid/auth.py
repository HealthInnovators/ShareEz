import json
import os

import requests
from requests.auth import HTTPBasicAuth

from ShareEz.utils.constants import TIMEOUT_PERIOD
from ShareEz.exceptions import AuthenticationErrorException, CannotFindCredentialException

ShareEz_CLIENT_ID = "ShareEz_CLIENT_ID"
ShareEz_CLIENT_SECRET = "ShareEz_CLIENT_SECRET"  # pragma: allowlist secret # nosec
ShareEz_URL = "ShareEz_URL"


class ShareEzAuth:
    def __init__(
        self, client_id: str = None, client_secret: str = None, url: str = None
    ) -> None:
        """
        The ShareEz auth class is a helper authentication class used to connect to your ShareEz API instance. The authentication values
        can be passed into the constructor but they default to reading them from your environment variables.

        Args:
            client_id (str, optional): Your ShareEz API client id token. Defaults to None.
            client_secret (str, optional): Your ShareEz API client secret token. Defaults to None.
            url (str, optional): The url where your ShareEz API is hosted. Defaults to None.
        """

        self.client_id = self.evaluate_inputs(client_id, ShareEz_CLIENT_ID)
        self.client_secret = self.evaluate_inputs(client_secret, ShareEz_CLIENT_SECRET)
        self.url = self.evaluate_inputs(url, ShareEz_URL)
        self.validate_credentials()

    def evaluate_inputs(self, value: str, environment_variable: str):
        if not value:
            value = os.environ.get(environment_variable)
            if not value:
                raise CannotFindCredentialException(
                    f"No value passed for {environment_variable}, could not authenticate to ShareEz"
                )
        return value

    @property
    def headers(self):
        return {"Content-Type": "application/x-www-form-urlencoded"}

    @property
    def payload(self):
        return {
            "grant_type": "client_credentials",
            "client_id": self.client_id,
        }

    def credentials_secret(self):
        return HTTPBasicAuth(self.client_id, self.client_secret)

    def request_token(self):
        response = requests.post(
            self.url + "/oauth2/token",
            auth=self.credentials_secret(),
            headers=self.headers,
            json=self.payload,
            timeout=TIMEOUT_PERIOD,
        )
        return response

    def validate_credentials(self):
        """
        Tests authentication to the ShareEz API.

        Raises:
            ShareEz.exceptions.AuthenticationErrorException: If no authorisation can be created.

        Returns:
            None: If authentication was successful.
        """
        if self.request_token().status_code != 200:
            raise AuthenticationErrorException(
                "Auth not configured, could not connect to instance of ShareEz"
            )

    def fetch_token(self):
        return json.loads(self.request_token().content.decode("utf-8"))["access_token"]
