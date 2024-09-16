The sdk is a standalone Python library that can provide easy programmatic access to the core ShareEz functionality. It can handle programmatic schema creation and updating using modern Python classes and data structures.

## Installation

Install the sdk easily with pip:

```
pip install ShareEz-sdk
```

### How to Use

Once installed into your project the first thing you will want to do is create an instance of the ShareEz class.

In order for your code to connect to ShareEz you will need your ShareEz client_id, client_secret and url values. By default the authentication module will try and read these from your environment variables as `ShareEz_CLIENT_ID`, `ShareEz_CLIENT_SECRET` and `ShareEz_URL` respectively. Alternatively you can create your own instance of the ShareEz authentication class.

```python
from ShareEz import ShareEz
from ShareEz import ShareEzAuth

ShareEz_authentication = ShareEzAuth()
ShareEz = ShareEz(auth=ShareEz_authentication)
```

If you do not want to use environment variables (however this is discouraged as secrets should always be kept safe), you can pass the values directly to the class as follows.

```python
ShareEz_authentication = ShareEzAuth(
    client_id=os.getenv("ShareEz_CLIENT_ID"),
    client_secret=os.getenv("ShareEz_CLIENT_SECRET"),
    url=os.getenv("ShareEz_URL"),
)
```

### Generate Schema

The sdk provides an easy and intuitive way to generate a schema based on a Pandas DataFrame you might have. The function returns a custom Pydantic Schema class type that matches a valid ShareEz schema. This can be used to programmatic information of the schema such as domain, dataset and lists of it's columns.

```python
import pandas as pd
from ShareEz import ShareEz

ShareEz = ShareEz()

raw_data = [{"a": 1, "b": 2, "c": 3}, {"a": 10, "b": 20, "c": 30}]
df = pd.DataFrame(raw_data)

schema = ShareEz.generate_schema(
    df=df, layer="layer", domain="domain", dataset="dataset", sensitivity="PUBLIC"
)

print("Domain ", schema.metadata.domain)
print("Columns ", schema.columns.dict())
```

### Download Data

The sdk provides an easy way to automatically download a specific dataset based on an optional version and query. The function returns the data in a pandas DataFrame format. See the example below for a basic example.

```python
import pandas as pd
from ShareEz import ShareEz

data = ShareEz.download_dataframe(
    layer="layer", domain="domain", dataset="dataset", version=1
)

print(data.info())
```

It is possible to pass a query to get more granular information about a dataset. We provide a Pydantic query class that can get passed into the download function. For more information on writing ShareEz compatible queries see [the documentation]() and the example below.

```python
import pandas as pd
from ShareEz import ShareEz
from ShareEz.items.query import Query

query = Query(
    select_columns=["column_to_select_one", "column_to_select_two"], limit="100"
)

data = ShareEz.download_dataframe(
    layer="layer", domain="domain", dataset="dataset", version=1, query=query
)

print(data.info())
```
