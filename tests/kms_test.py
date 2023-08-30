import datetime
import os

import bencodex

from src.kms import Signer

test_signer = Signer(kms_key=os.environ["KMS_KEY_ID"])


def test_address():
    assert test_signer.address == "0x2531e5e06cBD11aF54f98D39578990716fFC7dBa"


def test_transfer_assets() -> None:
    time_stamp = datetime.datetime(2022, 12, 31, tzinfo=datetime.timezone.utc)
    nonce = 2
    recipient = {
        "recipient": test_signer.address,
        "amount": {
            "quantity": 10,
            "decimalPlaces": 18,
            "ticker": "CRYSTAL",
        },
    }
    result = test_signer.transfer_assets(
        time_stamp,
        nonce,
        [recipient],
        "test",
        "https://9c-internal-rpc-1.nine-chronicles.com/graphql",
    )
    tx = bencodex.loads(result)
    assert tx[b"n"] == 2
    assert tx[b"t"] == "2022-12-31T00:00:00.000000Z"
    action = tx[b"a"][0]
    assert action["type_id"] == "transfer_assets2"
    plain_value = action["values"]
    assert plain_value["memo"] == "test"
