import datetime
import os

import bencodex

from src.kms import Signer

test_signer = Signer(kms_key=os.environ["KMS_KEY_ID"])


def test_address():
    assert test_signer.address == "0x2531e5e06cBD11aF54f98D39578990716fFC7dBa"


def test_sign_transaction():
    plain_value = "6475373a747970655f69647532323a756e6c6f61645f66726f6d5f6d795f6761726167657375363a76616c7565736475323a696431363adfaf5eed63601f4f9c1cb42375afee9275313a6c6c32303ac86d734bd2d5857cd25887db7dbbe252f12087c66e6c6c33323a3991e04dd808dc0bc24b21f5adb7bf1997312f8700daf1334bf34936e8a0813a69316565657531393a7369676e657220746573742062792079616e67656565"  # noqa
    time_stamp = datetime.datetime.utcnow()
    unsigned_local = test_signer.unsigned_tx(1, plain_value, time_stamp)
    sign = test_signer.sign_tx(bencodex.dumps(unsigned_local))
    signed_local = test_signer.attach_sign(unsigned_local, sign)
    assert signed_local[b"S"] == sign
    assert signed_local[b"n"] == 1
