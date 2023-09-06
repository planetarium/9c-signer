from gql import Client
from gql.dsl import DSLMutation, DSLQuery, DSLSchema, dsl_gql
from gql.transport.httpx import HTTPXTransport


def sign_transaction(url: str, unsigned_tx: bytes, signature: bytes) -> bytes:
    client = _get_client(url)
    with client as session:
        assert client.schema is not None
        ds = DSLSchema(client.schema)
        query = dsl_gql(
            DSLQuery(
                ds.StandaloneQuery.transaction.select(
                    ds.TransactionHeadlessQuery.signTransaction.args(
                        unsignedTransaction=unsigned_tx.hex(),
                        signature=signature.hex(),
                    )
                )
            )
        )
        result = session.execute(query)
        return bytes.fromhex(result["transaction"]["signTransaction"])


def unsigned_transaction(url: str, public_key: str, plain_value: str, nonce: int):
    client = _get_client(url)
    with client as session:
        assert client.schema is not None
        ds = DSLSchema(client.schema)
        query = dsl_gql(
            DSLQuery(
                ds.StandaloneQuery.transaction.select(
                    ds.TransactionHeadlessQuery.unsignedTransaction.args(
                        publicKey=public_key,
                        plainValue=plain_value,
                        nonce=nonce,
                    )
                )
            )
        )
        result = session.execute(query)
        return bytes.fromhex(result["transaction"]["unsignedTransaction"])


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
    return Client(transport=transport, fetch_schema_from_transport=True)
