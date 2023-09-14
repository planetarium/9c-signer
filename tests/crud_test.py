import time
import uuid
from typing import List, cast

import pytest
from redis import StrictRedis
from sqlalchemy.orm import Session

from src.crud import get_next_nonce
from src.models import Transaction


@pytest.mark.parametrize(
    "nonce_list, cached_nonce, expected",
    [
        ([], None, 0),
        ([], 1, 2),
        ([1, 2], None, 3),
        ([2, 3], None, 4),
        ([1, 4], None, 5),
        ([5], None, 6),
        ([4], 6, 7),
    ],
)
def test_get_next_nonce(
    db: Session,
    redisdb: StrictRedis,
    nonce_list: List[int],
    cached_nonce: int,
    expected: int,
):
    address = "0xCFCd6565287314FF70e4C4CF309dB701C43eA5bD"
    cache_key = f"{address}_nonce"
    if cached_nonce is not None:
        redisdb.set(cache_key, cached_nonce)
    assert redisdb.exists(cache_key) == int(cached_nonce is not None)
    for nonce in nonce_list:
        tx = Transaction(
            nonce=nonce,
            tx_id=str(nonce),
            signer=address,
            payload="payload",
            task_id=uuid.uuid4(),
        )
        db.add(tx)
    db.flush()
    # get nonce from db max value
    assert get_next_nonce(db, redisdb, address) == expected
    value: bytes = cast(bytes, redisdb.get(cache_key))
    # check cache
    assert int(value) == expected
    # check increase cache value
    assert get_next_nonce(db, redisdb, address, 1) == expected + 1
    # check cache expire
    time.sleep(1)
    assert not redisdb.exists(cache_key)
