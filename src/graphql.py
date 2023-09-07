from gql import Client
from gql.dsl import DSLMutation, DSLSchema, dsl_gql
from gql.transport.httpx import HTTPXTransport


def stage_transaction(url: str, payload: str) -> str:
    client = _get_client(url)
    with client as session:
        assert client.schema is not None
        ds = DSLSchema(client.schema)
        query = dsl_gql(
            DSLMutation(ds.StandaloneMutation.stageTransaction.args(payload=payload))
        )
        result = session.execute(query)
        return result["stageTransaction"]


def _get_client(url: str):
    transport = HTTPXTransport(url=url)
    return Client(
        transport=transport, fetch_schema_from_transport=True, execute_timeout=None
    )
