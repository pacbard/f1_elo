from typing import Any, Optional

import dlt
from dlt.sources.rest_api import (
    RESTAPIConfig,
    rest_api_resources
)
from dlt.sources.rest_api.typing import OffsetPaginator

@dlt.source(name="f1_data")
def f1_data_source(access_token: Optional[str] = dlt.secrets.value) -> Any:
    config: RESTAPIConfig = {
        "client": {
            "base_url": "https://api.jolpi.ca/ergast/f1/",
            "auth": (
                {
                    "type": "bearer",
                    "token": access_token,
                }
                if access_token
                else None
            ),
        },
        "resource_defaults": {
            "write_disposition": "merge",
        },
        "resources": [
            {
                "name": "seasons",
                "primary_key": "season",
                "endpoint": {
                    "path": "seasons",
                    "paginator": OffsetPaginator(
                        limit=30,
                        total_path="MRData.total"
                    )
                },
            },
            {
                "name": "drivers",
                "primary_key": ["driverId"],
                "endpoint": {
                    "path": "drivers",
                    "paginator": OffsetPaginator(
                        limit=30,
                        total_path="MRData.total"
                    )
                },
            },
            {
                "name": "races",
                "primary_key": ["season", "round"],
                "endpoint": {
                    "path": "races",
                    "paginator": OffsetPaginator(
                        limit=30,
                        total_path="MRData.total"
                    )
                },
            },
            {
                "name": "results",
                "primary_key": ["season", "round"],
                "endpoint": {
                    "path": "{season}/{round}/results",
                    "params": {
                        "season": {
                            "type": "resolve",
                            "resource": "races",
                            "field": "season",
                        },
                        "round": {
                            "type": "resolve",
                            "resource": "races",
                            "field": "round",
                        },
                    },
                    "paginator": OffsetPaginator(
                        limit=30,
                        total_path="MRData.total"
                    )
                },
            },
        ],
    }

    yield from rest_api_resources(config)


def load_f1_data() -> None:
    pipeline = dlt.pipeline(
        pipeline_name="f1_data",
        destination='duckdb',
        dataset_name="f1",
    )

    load_info = pipeline.run(f1_data_source())
    print(load_info)

if __name__ == "__main__":
    # Run pipeline
    load_f1_data()
