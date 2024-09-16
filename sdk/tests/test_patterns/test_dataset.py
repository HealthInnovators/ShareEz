from mock import MagicMock, Mock, patch, call
import pytest
from pandas import DataFrame
from requests_mock import Mocker

from ShareEz.items.schema import Owner, SchemaMetadata, Schema, SensitivityLevel, Column
from ShareEz.patterns.dataset import (
    upload_and_create_dataset,
    update_schema_to_dataframe,
)
from ShareEz.exceptions import (
    DataFrameUploadValidationException,
    DatasetNotFoundException,
)
from ShareEz import ShareEz


class TestData:
    def setup_method(self):
        self.metadata = SchemaMetadata(
            layer="raw",
            domain="test",
            dataset="ShareEz_sdk",
            sensitivity=SensitivityLevel.PUBLIC,
            owners=[Owner(name="test", email="test@email.com")],
        )

        self.mock_schema = Schema(
            metadata=self.metadata,
            columns=[
                Column(
                    name="column_a",
                    partition_index=None,
                    data_type="object",
                    allow_null=True,
                    format=None,
                ),
                Column(
                    name="column_b",
                    partition_index=None,
                    data_type="object",
                    allow_null=True,
                    format=None,
                ),
                Column(
                    name="column_c",
                    partition_index=None,
                    data_type="object",
                    allow_null=True,
                    format=None,
                ),
            ],
        )

        self.df = DataFrame(
            {
                "column_a": ["one", "two", "three"],
                "column_b": ["one", "two", "three"],
                "column_c": ["one", "two", "three"],
            }
        )

    def test_upload_and_create_dataset_success(self, ShareEz: ShareEz):
        ShareEz.upload_dataframe = Mock()
        ShareEz.create_schema = Mock()
        ShareEz.update_schema = Mock()

        upload_and_create_dataset(ShareEz, self.metadata, self.df)
        ShareEz.upload_dataframe.assert_called_once_with(
            self.metadata.layer,
            self.metadata.domain,
            self.metadata.dataset,
            self.df,
            wait_to_complete=True,
        )
        ShareEz.create_schema.assert_not_called()
        ShareEz.update_schema.assert_not_called()

    def test_upload_and_create_dataset_dataset_not_found(self, ShareEz: ShareEz):
        ShareEz.upload_dataframe = Mock(
            side_effect=[DatasetNotFoundException("dummy", "data"), None]
        )
        ShareEz.generate_schema = Mock(return_value=self.mock_schema)
        ShareEz.create_schema = Mock()
        upload_and_create_dataset(ShareEz, self.metadata, self.df)

        ShareEz.generate_schema.assert_called_once_with(
            self.df,
            self.metadata.layer,
            self.metadata.domain,
            self.metadata.dataset,
            self.metadata.sensitivity,
        )
        ShareEz.create_schema.assert_called_once_with(self.mock_schema)

        expected_call = call(
            self.metadata.layer,
            self.metadata.domain,
            self.metadata.dataset,
            self.df,
            wait_to_complete=True,
        )
        ShareEz.upload_dataframe.assert_has_calls([expected_call, expected_call])

    def test_upload_and_create_dataset_do_not_upgrade_schema_on_fail(
        self, ShareEz: ShareEz
    ):
        ShareEz.upload_dataframe = Mock(
            side_effect=[DataFrameUploadValidationException("dummy", "data"), None]
        )

        with pytest.raises(DataFrameUploadValidationException):
            upload_and_create_dataset(
                ShareEz, self.metadata, self.df, upgrade_schema_on_fail=False
            )
        ShareEz.upload_dataframe.assert_called_once_with(
            self.metadata.layer,
            self.metadata.domain,
            self.metadata.dataset,
            self.df,
            wait_to_complete=True,
        )

    @patch("ShareEz.patterns.dataset.update_schema_to_dataframe")
    def test_upload_and_create_dataset_upgrade_schema_on_fail(
        self, mocked_update_schema_to_dataframe: MagicMock, ShareEz: ShareEz
    ):
        ShareEz.upload_dataframe = Mock(
            side_effect=[DataFrameUploadValidationException("dummy", "data"), None]
        )

        upload_and_create_dataset(
            ShareEz, self.metadata, self.df, upgrade_schema_on_fail=True
        )
        mocked_update_schema_to_dataframe.assert_called_once_with(
            ShareEz, self.metadata, self.df
        )

        expected_call = call(
            self.metadata.layer,
            self.metadata.domain,
            self.metadata.dataset,
            self.df,
            wait_to_complete=True,
        )
        ShareEz.upload_dataframe.assert_has_calls([expected_call, expected_call])

    def test_update_schema_to_dataframe(self, requests_mock: Mocker, ShareEz: ShareEz):
        new_columns = [
            Column(
                name="column_a",
                partition_index=None,
                data_type="float64",  # NOTE: Change in data type for column
                allow_null=True,
                format=None,
            ),
            Column(
                name="column_b",
                partition_index=None,
                data_type="object",
                allow_null=True,
                format=None,
            ),
            Column(
                name="column_c",
                partition_index=None,
                data_type="object",
                allow_null=True,
                format=None,
            ),
        ]

        new_schema = Schema(metadata=self.mock_schema.metadata, columns=new_columns)
        ShareEz.generate_schema = Mock(return_value=new_schema)
        ShareEz.update_schema = Mock()

        update_schema_to_dataframe(ShareEz, self.metadata, self.df)

        ShareEz.generate_schema.assert_called_once_with(
            self.df,
            self.metadata.layer,
            self.metadata.domain,
            self.metadata.dataset,
            self.metadata.sensitivity,
        )
        ShareEz.update_schema.assert_called_once_with(new_schema)
