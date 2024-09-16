from mock import Mock, call
import pytest
import io
import pandas as pd
from requests_mock import Mocker

from ShareEz import ShareEz
from ShareEz.items.schema import Schema
from ShareEz.exceptions import (
    DataFrameUploadFailedException,
    JobFailedException,
    SchemaGenerationFailedException,
    SchemaAlreadyExistsException,
    SchemaCreateFailedException,
    SchemaUpdateFailedException,
    UnableToFetchJobStatusException,
    DatasetInfoFailedException,
    InvalidPermissionsException,
    SubjectNotFoundException,
    SubjectAlreadyExistsException,
    DatasetNotFoundException,
    InvalidDomainNameException,
    DomainConflictException,
    ClientDoesNotHaveUserAdminPermissionsException,
    ClientDoesNotHaveDataAdminPermissionsException
)
from .conftest import ShareEz_URL, ShareEz_TOKEN

DUMMY_SCHEMA = {
    "metadata": {
        "layer": "raw",
        "domain": "test",
        "dataset": "ShareEz_sdk",
        "sensitivity": "PUBLIC",
        "owners": [{"name": "Test", "email": "test@email.com"}],
        "version": None,
        "key_value_tags": None,
        "key_only_tags": None,
    },
    "columns": [
        {
            "name": "column_a",
            "data_type": "object",
            "partition_index": None,
            "allow_null": True,
            "format": None,
        },
        {
            "name": "column_b",
            "data_type": "object",
            "partition_index": None,
            "allow_null": True,
            "format": None,
        },
    ],
}


class TestShareEz:
    @pytest.mark.usefixtures("ShareEz")
    def test_generate_headers(self, ShareEz: ShareEz):
        expected = {"Authorization": f"Bearer {ShareEz_TOKEN}"}

        assert expected == ShareEz.generate_headers()

    @pytest.mark.usefixtures("requests_mock", "ShareEz")
    def test_list_datasets(self, requests_mock: Mocker, ShareEz: ShareEz):
        expected = {"response": "dummy"}
        requests_mock.post(f"{ShareEz_URL}/datasets", json=expected)

        res = ShareEz.list_datasets()
        assert res == expected

    @pytest.mark.usefixtures("requests_mock", "ShareEz")
    def test_fetch_job_progress_success(self, requests_mock: Mocker, ShareEz: ShareEz):
        job_id = 1234
        expected = {"response": "dummy"}

        requests_mock.get(f"{ShareEz_URL}/jobs/{job_id}", json=expected)
        res = ShareEz.fetch_job_progress(job_id)
        assert res == expected

    @pytest.mark.usefixtures("requests_mock", "ShareEz")
    def test_fetch_job_progress_fail(self, requests_mock: Mocker, ShareEz: ShareEz):
        job_id = 1234
        expected = {"response": "error"}
        requests_mock.get(f"{ShareEz_URL}/jobs/{job_id}", status_code=400, json=expected)

        with pytest.raises(UnableToFetchJobStatusException):
            ShareEz.fetch_job_progress(job_id)

    @pytest.mark.usefixtures("ShareEz")
    def test_wait_for_job_outcome_success(self, ShareEz: ShareEz):
        ShareEz.fetch_job_progress = Mock(
            side_effect=[{"status": "IN PROGRESS"}, {"status": "SUCCESS"}]
        )
        job_id = 1234

        res = ShareEz.wait_for_job_outcome(job_id, interval=0.01)
        assert res is None
        expected_calls = [call(job_id), call(job_id)]
        assert ShareEz.fetch_job_progress.call_args_list == expected_calls

    @pytest.mark.usefixtures("ShareEz")
    def test_wait_for_job_outcome_failure(self, ShareEz: ShareEz):
        ShareEz.fetch_job_progress = Mock(
            side_effect=[{"status": "IN PROGRESS"}, {"status": "FAILED"}]
        )
        job_id = 1234

        with pytest.raises(JobFailedException):
            ShareEz.wait_for_job_outcome(job_id, interval=0.01)
            expected_calls = [call(job_id), call(job_id)]
            assert ShareEz.fetch_job_progress.call_args_list == expected_calls

    @pytest.mark.usefixtures("requests_mock", "ShareEz")
    def test_download_dataframe_success(self, requests_mock: Mocker, ShareEz: ShareEz):
        layer = "raw"
        domain = "test_domain"
        dataset = "test_dataset"
        requests_mock.post(
            f"{ShareEz_URL}/datasets/{layer}/{domain}/{dataset}/query",
            json={
                "0": {"column1": "value1", "column2": "value2"},
                "2": {"column1": "value3", "column2": "value4"},
                "3": {"column1": "value5", "column2": "value6"},
            },
            status_code=200,
        )
        res = ShareEz.download_dataframe(layer, domain, dataset)
        assert res.shape == (3, 2)
        assert list(res.columns) == ["column1", "column2"]

    @pytest.mark.usefixtures("requests_mock", "ShareEz")
    def test_download_dataframe_success_with_version(
        self, requests_mock: Mocker, ShareEz: ShareEz
    ):
        layer = "raw"
        domain = "test_domain"
        dataset = "test_dataset"
        version = "5"
        requests_mock.post(
            f"{ShareEz_URL}/datasets/{layer}/{domain}/{dataset}/query?version=5",
            json={
                "0": {"column1": "value1", "column2": "value2"},
                "2": {"column1": "value3", "column2": "value4"},
                "3": {"column1": "value5", "column2": "value6"},
            },
            status_code=200,
        )
        res = ShareEz.download_dataframe(layer, domain, dataset, version)
        assert res.shape == (3, 2)
        assert list(res.columns) == ["column1", "column2"]

    @pytest.mark.usefixtures("requests_mock", "ShareEz")
    def test_upload_dataframe_success_after_waiting(
        self, requests_mock: Mocker, ShareEz: ShareEz
    ):
        layer = "raw"
        domain = "test_domain"
        dataset = "test_dataset"
        job_id = 1234
        df = pd.DataFrame()
        requests_mock.post(
            f"{ShareEz_URL}/datasets/{layer}/{domain}/{dataset}",
            json={"details": {"job_id": job_id}},
            status_code=202,
        )
        ShareEz.wait_for_job_outcome = Mock()
        ShareEz.convert_dataframe_for_file_upload = Mock(return_value={})

        res = ShareEz.upload_dataframe(layer, domain, dataset, df)
        assert res == "Success"
        ShareEz.wait_for_job_outcome.assert_called_once_with(job_id)
        ShareEz.convert_dataframe_for_file_upload.assert_called_once_with(df)

    @pytest.mark.usefixtures("requests_mock", "ShareEz")
    def test_upload_dataframe_success_no_waiting(
        self, requests_mock: Mocker, ShareEz: ShareEz
    ):
        layer = "raw"
        domain = "test_domain"
        dataset = "test_dataset"
        job_id = 1234
        df = pd.DataFrame()
        requests_mock.post(
            f"{ShareEz_URL}/datasets/{layer}/{domain}/{dataset}",
            json={"details": {"job_id": job_id}},
            status_code=202,
        )
        ShareEz.convert_dataframe_for_file_upload = Mock(return_value={})

        res = ShareEz.upload_dataframe(layer, domain, dataset, df, wait_to_complete=False)
        assert res == job_id
        ShareEz.convert_dataframe_for_file_upload.assert_called_once_with(df)

    @pytest.mark.usefixtures("requests_mock", "ShareEz")
    def test_upload_dataframe_failure(self, requests_mock: Mocker, ShareEz: ShareEz):
        layer = "raw"
        domain = "test_domain"
        dataset = "test_dataset"
        job_id = 1234
        df = pd.DataFrame()
        requests_mock.post(
            f"{ShareEz_URL}/datasets/{layer}/{domain}/{dataset}",
            json={"details": {"job_id": job_id}},
            status_code=400,
        )
        ShareEz.convert_dataframe_for_file_upload = Mock(return_value={})

        with pytest.raises(DataFrameUploadFailedException):
            ShareEz.upload_dataframe(layer, domain, dataset, df, wait_to_complete=False)
            ShareEz.convert_dataframe_for_file_upload.assert_called_once_with(df)

    @pytest.mark.usefixtures("requests_mock", "ShareEz")
    def test_fetch_dataset_info_success(self, requests_mock: Mocker, ShareEz: ShareEz):
        layer = "raw"
        domain = "test_domain"
        dataset = "test_dataset"
        mocked_response = {"data": "dummy"}
        requests_mock.get(
            f"{ShareEz_URL}/datasets/{layer}/{domain}/{dataset}/info",
            json=mocked_response,
            status_code=200,
        )

        res = ShareEz.fetch_dataset_info(layer, domain, dataset)
        assert res == mocked_response

    @pytest.mark.usefixtures("requests_mock", "ShareEz")
    def test_fetch_dataset_info_failure(self, requests_mock: Mocker, ShareEz: ShareEz):
        layer = "raw"
        domain = "test_domain"
        dataset = "test_dataset"
        mocked_response = {"details": "dummy"}
        requests_mock.get(
            f"{ShareEz_URL}/datasets/{layer}/{domain}/{dataset}/info",
            json=mocked_response,
            status_code=422,
        )

        with pytest.raises(DatasetInfoFailedException):
            ShareEz.fetch_dataset_info(layer, domain, dataset)

    @pytest.mark.usefixtures("ShareEz")
    def test_convert_dataframe_for_file_upload(self, ShareEz: ShareEz):
        df = pd.DataFrame()
        res = ShareEz.convert_dataframe_for_file_upload(df)
        filename = res["file"][0]
        data = io.BytesIO(res["file"][1])
        df = pd.read_parquet(data)

        assert filename.startswith("ShareEz-sdk") and filename.endswith(".parquet")
        assert len(df) == 0

    @pytest.mark.usefixtures("requests_mock", "ShareEz")
    def test_generate_schema_success(self, requests_mock: Mocker, ShareEz: ShareEz):
        layer = "raw"
        domain = "test_domain"
        dataset = "test_dataset"
        sensitivity = "PUBLIC"
        df = pd.DataFrame()
        mocked_response = {
            "metadata": {
                "layer": "raw",
                "domain": "test",
                "dataset": "ShareEz_sdk",
                "sensitivity": "PUBLIC",
                "owners": [{"name": "Test", "email": "test@email.com"}],
                "version": None,
                "key_value_tags": None,
                "key_only_tags": None,
            },
            "columns": [
                {
                    "name": "column_a",
                    "data_type": "object",
                    "partition_index": None,
                    "allow_null": True,
                    "format": None,
                },
                {
                    "name": "column_b",
                    "data_type": "object",
                    "partition_index": None,
                    "allow_null": True,
                    "format": None,
                },
            ],
        }
        requests_mock.post(
            f"{ShareEz_URL}/schema/{layer}/{sensitivity}/{domain}/{dataset}/generate",
            json=mocked_response,
            status_code=200,
        )

        res = ShareEz.generate_schema(df, layer, domain, dataset, sensitivity)
        assert res.metadata.layer == "raw"
        assert res.metadata.domain == "test"
        assert res.metadata.dataset == "ShareEz_sdk"
        assert res.columns[0].name == "column_a"
        assert res.columns[1].name == "column_b"

    @pytest.mark.usefixtures("requests_mock", "ShareEz")
    def test_generate_schema_failure(self, requests_mock: Mocker, ShareEz: ShareEz):
        layer = "raw"
        domain = "test_domain"
        dataset = "test_dataset"
        sensitivity = "PUBLIC"
        df = pd.DataFrame()
        mocked_response = {"data": "dummy"}
        requests_mock.post(
            f"{ShareEz_URL}/schema/{layer}/{sensitivity}/{domain}/{dataset}/generate",
            json=mocked_response,
            status_code=400,
        )
        with pytest.raises(SchemaGenerationFailedException):
            ShareEz.generate_schema(df, layer, domain, dataset, sensitivity)

    @pytest.mark.usefixtures("requests_mock", "ShareEz")
    def test_create_schema_success(self, requests_mock: Mocker, ShareEz: ShareEz):
        schema = Schema(**DUMMY_SCHEMA)
        mocked_response = {"data": "dummy"}
        requests_mock.post(f"{ShareEz_URL}/schema", json=mocked_response, status_code=201)
        res = ShareEz.create_schema(schema)
        assert res is None

    @pytest.mark.usefixtures("requests_mock", "ShareEz")
    def test_create_schema_failure_schema_already_exists(
        self, requests_mock: Mocker, ShareEz: ShareEz
    ):
        schema = Schema(**DUMMY_SCHEMA)
        mocked_response = {"data": "dummy"}
        requests_mock.post(f"{ShareEz_URL}/schema", json=mocked_response, status_code=409)
        with pytest.raises(SchemaAlreadyExistsException):
            ShareEz.create_schema(schema)

    @pytest.mark.usefixtures("requests_mock", "ShareEz")
    def test_create_schema_failure(self, requests_mock: Mocker, ShareEz: ShareEz):
        schema = Schema(**DUMMY_SCHEMA)
        mocked_response = {"data": "dummy"}
        requests_mock.post(f"{ShareEz_URL}/schema", json=mocked_response, status_code=400)
        with pytest.raises(SchemaCreateFailedException):
            ShareEz.create_schema(schema)

    @pytest.mark.usefixtures("requests_mock", "ShareEz")
    def test_update_schema_success(self, requests_mock: Mocker, ShareEz: ShareEz):
        schema = Schema(**DUMMY_SCHEMA)
        mocked_response = {"data": "dummy"}
        requests_mock.put(f"{ShareEz_URL}/schema", json=mocked_response, status_code=200)
        res = ShareEz.update_schema(schema)
        assert res == mocked_response

    @pytest.mark.usefixtures("requests_mock", "ShareEz")
    def test_update_schema_failure(self, requests_mock: Mocker, ShareEz: ShareEz):
        schema = Schema(**DUMMY_SCHEMA)
        mocked_response = {"data": "dummy"}
        requests_mock.put(f"{ShareEz_URL}/schema", json=mocked_response, status_code=400)
        with pytest.raises(SchemaUpdateFailedException):
            ShareEz.update_schema(schema)

    @pytest.mark.usefixtures("requests_mock", "ShareEz")
    def test_create_client_success(self, requests_mock: Mocker, ShareEz: ShareEz):
        mocked_response = {
            "client_name": "client",
            "permissions": ["READ_ALL"],
            "client_id": "xxx-yyy-zzz",
            "client_secret": "1234567",
        }
        requests_mock.post(f"{ShareEz_URL}/client", json=mocked_response, status_code=201)
        res = ShareEz.create_client("client", ["READ_ALL"])
        assert res == mocked_response

    @pytest.mark.usefixtures("requests_mock", "ShareEz")
    def test_create_client_failure(self, requests_mock: Mocker, ShareEz: ShareEz):
        mocked_response = {"data": "dummy"}
        requests_mock.post(f"{ShareEz_URL}/client", json=mocked_response, status_code=400)
        with pytest.raises(SubjectAlreadyExistsException):
            ShareEz.create_client("client", ["READ_ALL"])

    @pytest.mark.usefixtures("requests_mock", "ShareEz")
    def test_delete_client_success(self, requests_mock: Mocker, ShareEz: ShareEz):
        mocked_response = {"data": "dummy"}
        requests_mock.delete(
            f"{ShareEz_URL}/client/xxx-yyy-zzz", json=mocked_response, status_code=200
        )
        res = ShareEz.delete_client("xxx-yyy-zzz")
        assert res is None

    @pytest.mark.usefixtures("requests_mock", "ShareEz")
    def test_delete_client_failure(self, requests_mock: Mocker, ShareEz: ShareEz):
        mocked_response = {"data": "dummy"}
        requests_mock.delete(
            f"{ShareEz_URL}/client/xxx-yyy-zzz", json=mocked_response, status_code=400
        )
        with pytest.raises(SubjectNotFoundException):
            ShareEz.delete_client("xxx-yyy-zzz")

    @pytest.mark.usefixtures("requests_mock", "ShareEz")
    def test_update_subject_permissions_success(
        self, requests_mock: Mocker, ShareEz: ShareEz
    ):
        mocked_response = {"data": "dummy"}
        requests_mock.put(
            f"{ShareEz_URL}/subject/permissions", json=mocked_response, status_code=200
        )
        res = ShareEz.update_subject_permissions("xxx-yyy-zzz", ["READ_ALL"])
        assert res == mocked_response

    @pytest.mark.usefixtures("requests_mock", "ShareEz")
    def test_update_subject_permissions_failure(
        self, requests_mock: Mocker, ShareEz: ShareEz
    ):
        mocked_response = {"data": "dummy"}
        requests_mock.put(
            f"{ShareEz_URL}/subject/permissions", json=mocked_response, status_code=400
        )
        with pytest.raises(InvalidPermissionsException):
            ShareEz.update_subject_permissions("xxx-yyy-zzz", ["READ_ALL"])

    @pytest.mark.usefixtures("requests_mock", "ShareEz")
    def test_create_protected_domain_invalid_name_failure(
        self, requests_mock: Mocker, ShareEz: ShareEz
    ):
        mocked_response = {
            "details": "The value set for domain [dummy] can only contain alphanumeric and underscore `_` characters and must start with an alphabetic character"
        }
        requests_mock.post(
            f"{ShareEz_URL}/protected_domains/dummy",
            json=mocked_response,
            status_code=400,
        )
        with pytest.raises(InvalidDomainNameException) as exc_info:
            ShareEz.create_protected_domain("dummy")

        assert (
            str(exc_info.value)
            == "The value set for domain [dummy] can only contain alphanumeric and underscore `_` characters and must start with an alphabetic character"
        )

    @pytest.mark.usefixtures("requests_mock", "ShareEz")
    def test_create_protected_domain_conflict_failure(
        self, requests_mock: Mocker, ShareEz: ShareEz
    ):
        mocked_response = {"details": "The protected domain, [dummy] already exists"}
        requests_mock.post(
            f"{ShareEz_URL}/protected_domains/dummy",
            json=mocked_response,
            status_code=409,
        )
        with pytest.raises(DomainConflictException) as exc_info:
            ShareEz.create_protected_domain("dummy")

        assert str(exc_info.value) == "The protected domain, [dummy] already exists"

    @pytest.mark.usefixtures("requests_mock", "ShareEz")
    def test_create_protected_domain_success(self, requests_mock: Mocker, ShareEz: ShareEz):
        mocked_response = {"data": "dummy"}
        requests_mock.post(
            f"{ShareEz_URL}/protected_domains/dummy",
            json=mocked_response,
            status_code=201,
        )
        res = ShareEz.create_protected_domain("dummy")
        assert res is None
        
    @pytest.mark.usefixtures("requests_mock", "ShareEz")
    def test_create_user_success(self, requests_mock: Mocker, ShareEz: ShareEz):
        mocked_response = {
            "username": "user",
            "email": "user",
            "permissions": ["READ_ALL"],
            "user_id": "xxx-yyy-zzz"
        }
        requests_mock.post(f"{ShareEz_URL}/user", json=mocked_response, status_code=201)
        res = ShareEz.create_user("user", "user@user.com", ["READ_ALL"])
        assert res == mocked_response

    @pytest.mark.usefixtures("requests_mock", "ShareEz")
    def test_create_user_failure_subjectalreadyexists(self, requests_mock: Mocker, ShareEz: ShareEz):
        mocked_response = {"details": "The user 'user' or email 'user@user.com' already exist"}
        requests_mock.post(f"{ShareEz_URL}/user", json=mocked_response, status_code=400)
        with pytest.raises(SubjectAlreadyExistsException):
            ShareEz.create_user("user", "user@user.com", ["READ_ALL"])
    
    @pytest.mark.usefixtures("requests_mock", "ShareEz")
    def test_create_user_failure_invalidpermissions(self, requests_mock: Mocker, ShareEz: ShareEz):
        mocked_response = {"details": "One or more of the provided permissions is invalid or duplicated"}
        requests_mock.post(f"{ShareEz_URL}/user", json=mocked_response, status_code=400)
        with pytest.raises(InvalidPermissionsException):
            ShareEz.create_user("user", "user@user.com", ["READ_ALL"])

    @pytest.mark.usefixtures("requests_mock", "ShareEz")
    def test_create_user_failure_ClientDoesNotHaveUserAdminPermissions(self, requests_mock: Mocker, ShareEz: ShareEz):
        mocked_response = {"details": "data"}
        requests_mock.post(f"{ShareEz_URL}/user", json=mocked_response, status_code=401)
        with pytest.raises(ClientDoesNotHaveUserAdminPermissionsException):
            ShareEz.create_user("user", "user@user.com", ["READ_ALL"])

    @pytest.mark.usefixtures("requests_mock", "ShareEz")
    def test_delete_user_success(self, requests_mock: Mocker, ShareEz: ShareEz):
        mocked_response = {
            "username": "user",
            "user_id": "xxx-yyy-zzz"
        }
        requests_mock.delete(
            f"{ShareEz_URL}/user", json=mocked_response, status_code=200
        )
        res = ShareEz.delete_user("user", "xxx-yyy-zzz")
        assert res == mocked_response

    @pytest.mark.usefixtures("requests_mock", "ShareEz")
    def test_delete_user_failure_SubjectNotFound(self, requests_mock: Mocker, ShareEz: ShareEz):
        mocked_response = {"data": "dummy"}
        requests_mock.delete(
            f"{ShareEz_URL}/user", json=mocked_response, status_code=400
        )
        with pytest.raises(SubjectNotFoundException):
            ShareEz.delete_user("user", "xxx-yyy-zzz")

    @pytest.mark.usefixtures("requests_mock", "ShareEz")
    def test_delete_user_failure_ClientDoesNotHaveUserAdminPermissions(self, requests_mock: Mocker, ShareEz: ShareEz):
        mocked_response = {"details": "User xxx-yyy-zzz does not have permissions that grant access to the endpoint scopes [<Action.USER_ADMIN: 'USER_ADMIN'>]"}
        requests_mock.delete(
            f"{ShareEz_URL}/user", json=mocked_response, status_code=401
        )
        with pytest.raises(ClientDoesNotHaveUserAdminPermissionsException):
            ShareEz.delete_user("user", "xxx-yyy-zzz")

    @pytest.mark.usefixtures("requests_mock", "ShareEz")
    def test_list_subjects_success(self, requests_mock: Mocker, ShareEz: ShareEz):
        expected = {"response": "dummy"}
        requests_mock.get(f"{ShareEz_URL}/subjects", json=expected)

        res = ShareEz.list_subjects()
        assert res == expected

    @pytest.mark.usefixtures("requests_mock", "ShareEz")
    def test_list_subjects_failure_ClientDoesNotHaveUserAdminPermissions(self, requests_mock: Mocker, ShareEz: ShareEz):
        expected = {"details": "User xxx-yyy-zzz does not have permissions that grant access to the endpoint scopes [<Action.USER_ADMIN: 'USER_ADMIN'>]"}
        requests_mock.get(f"{ShareEz_URL}/subjects", json=expected, status_code=401)
        with pytest.raises(ClientDoesNotHaveUserAdminPermissionsException):
            ShareEz.list_subjects()

    @pytest.mark.usefixtures("requests_mock", "ShareEz")
    def test_list_layers(self, requests_mock: Mocker, ShareEz: ShareEz):
        expected = {"response": "dummy"}
        requests_mock.get(f"{ShareEz_URL}/layers", json=expected)

        res = ShareEz.list_layers()
        assert res == expected

    @pytest.mark.usefixtures("requests_mock", "ShareEz")
    def test_list_protected_domains(self, requests_mock: Mocker, ShareEz: ShareEz):
        expected = {"details": "User xxx-yyy-zzz does not have permissions that grant access to the endpoint scopes [<Action.USER_ADMIN: 'USER_ADMIN'>]"}
        requests_mock.get(f"{ShareEz_URL}/protected_domains", json=expected)

        res = ShareEz.list_protected_domains()
        assert res == expected

    @pytest.mark.usefixtures("requests_mock", "ShareEz")
    def test_list_protected_domains_failure_ClientDoesNotHaveUserAdminPermissions(self, requests_mock: Mocker, ShareEz: ShareEz):
        expected = {"details": "User xxx-yyy-zzz does not have permissions that grant access to the endpoint scopes [<Action.USER_ADMIN: 'USER_ADMIN'>]"}
        requests_mock.get(f"{ShareEz_URL}/protected_domains", json=expected, status_code=401)
        with pytest.raises(ClientDoesNotHaveUserAdminPermissionsException):
            ShareEz.list_protected_domains()

    @pytest.mark.usefixtures("requests_mock", "ShareEz")
    def test_delete_dataset_success(self, requests_mock: Mocker, ShareEz: ShareEz):
        layer = "raw"
        domain = "test_domain"
        dataset = "test_dataset"
        mocked_response = {'details': '{dataset} has been deleted.'}
        requests_mock.delete(
            f"{ShareEz_URL}/datasets/{layer}/{domain}/{dataset}",
              json=mocked_response, 
              status_code=202
        )
        res = ShareEz.delete_dataset(layer, domain, dataset)
        assert res == mocked_response

    @pytest.mark.usefixtures("requests_mock", "ShareEz")
    def test_delete_dataset_failure_DatasetNotFound(self, requests_mock: Mocker, ShareEz: ShareEz):
        layer = "raw"
        domain = "test_domain"
        dataset = "test_dataset"
        mocked_response = {"response": "dummy"}
        requests_mock.delete(
            f"{ShareEz_URL}/datasets/{layer}/{domain}/{dataset}", 
            json=mocked_response, 
            status_code=400
        )
        with pytest.raises(DatasetNotFoundException):
            ShareEz.delete_dataset(layer, domain, dataset)

    @pytest.mark.usefixtures("requests_mock", "ShareEz")
    def test_delete_dataset_failure_ClientDoesNotHaveDataAdminPermissions(self, requests_mock: Mocker, ShareEz: ShareEz):
        layer = "raw"
        domain = "test_domain"
        dataset = "test_dataset"
        mocked_response = {'details': "User xxx-yyy-zzz does not have permissions that grant access to the endpoint scopes [<Action.DATA_ADMIN: 'DATA_ADMIN'>]"}
        requests_mock.delete(
            f"{ShareEz_URL}/datasets/{layer}/{domain}/{dataset}", 
            json=mocked_response, 
            status_code=401
        )
        with pytest.raises(ClientDoesNotHaveDataAdminPermissionsException):
            ShareEz.delete_dataset(layer, domain, dataset)
