import os

from src.kms import Signer

test_signer = Signer(kms_key=os.environ["KMS_KEY_ID"])


def test_address():
    assert test_signer.address == "0x2531e5e06cBD11aF54f98D39578990716fFC7dBa"
