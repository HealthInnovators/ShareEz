With the sdk we ship useful functions that handle common programmatic functionality for ShareEz.

## Dataframe Upload

Below is a simple example for uploading a Pandas DataFrame to the API.

```python
import pandas as pd
from ShareEz import ShareEz
from ShareEz.patterns import dataset
from ShareEz.items.schema import SchemaMetadata, SensitivityLevel, Owner
from ShareEz.exceptions import DataFrameUploadValidationException

ShareEz = ShareEz()

raw_data = [{"a": 1, "b": 2, "c": 3}, {"a": 10, "b": 20, "c": 30}]
df = pd.DataFrame(raw_data)

metadata = SchemaMetadata(
    layer="default",
    domain="mydomain",
    dataset="mydataset",
    owners=[Owner(name="myname", email="myemail@email.com")],
    sensitivity=SensitivityLevel.PUBLIC.value,
)

try:
    dataset.upload_and_create_dataset(
        ShareEz=ShareEz, df=df, metadata=metadata, upgrade_schema_on_fail=False
    )
except DataFrameUploadValidationException:
    print("Incorrect DataFrame schema")
```

## Update Schema

Now going forward say for instance we now expect that for column c we can expect some values to be floating points, we want to update the schema.

```python
import pandas as pd
from ShareEz import ShareEz
from ShareEz.patterns import dataset
from ShareEz.items.schema import SchemaMetadata, SensitivityLevel, Owner, Column
from ShareEz.exceptions import ColumnNotDifferentException

ShareEz = ShareEz()

raw_data = [{"a": 1, "b": 2, "c": 3}, {"a": 10, "b": 20, "c": 30}]
df = pd.DataFrame(raw_data)

metadata = SchemaMetadata(
    layer="default",
    domain="mydomain",
    dataset="mydataset",
    owners=[Owner(name="myname", email="myemail@email.com")],
    _sensitivity=SensitivityLevel.PUBLIC.value,
)

try:
    dataset.update_schema_to_dataframe(
        ShareEz=ShareEz,
        df=df,
        metadata=metadata,
        new_columns=[Column(name="c", data_type="Float64")],
    )
except ColumnNotDifferentException:
    print("Columns not different.")
```
