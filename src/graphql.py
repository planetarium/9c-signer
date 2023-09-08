from gql import Client
from gql.dsl import DSLMutation, DSLQuery, DSLSchema, dsl_gql
from gql.transport.httpx import HTTPXTransport

from src.schemas import TransactionResult


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


def check_transaction_result(url: str, tx_id: str) -> TransactionResult:
    client = _get_client(url)
    with client as session:
        assert client.schema is not None
        ds = DSLSchema(client.schema)
        query = dsl_gql(
            DSLQuery(
                ds.StandaloneQuery.transaction.select(
                    ds.TransactionHeadlessQuery.transactionResult.args(
                        txId=tx_id
                    ).select(ds.TxResultType.txStatus, ds.TxResultType.exceptionName)
                )
            )
        )
        result = session.execute(query)
        tx_result = result["transaction"]["transactionResult"]
        return TransactionResult(**tx_result)


def _get_client(url: str):
    transport = HTTPXTransport(url=url)
    return Client(
        transport=transport, fetch_schema_from_transport=True, execute_timeout=None
    )
