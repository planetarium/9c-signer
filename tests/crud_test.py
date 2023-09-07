import uuid
from typing import List, Optional, cast

import pytest
from redis import StrictRedis
from sqlalchemy.orm import Session

from src.crud import get_next_nonce
from src.models import Transaction


@pytest.mark.parametrize(
    "nonce_list, expected",
    [
        ([], 1),
        ([1, 2], 3),
        ([2, 3], 4),
        ([1, 4], 5),
        ([5], 6),
    ],
)
def test_get_next_nonce_from_db(
    db: Session, redisdb: StrictRedis, nonce_list: List[int], expected: int
):
    address = "0xCFCd6565287314FF70e4C4CF309dB701C43eA5bD"
    cache_key = f"{address}_nonce"
    assert not redisdb.exists(cache_key)
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
    assert get_next_nonce(db, redisdb, address) == expected + 1


@pytest.mark.parametrize(
    "nonce, expected",
    [
        (None, 1),
        (2, 3),
    ],
)
def get_next_nonce_from_cache(
    db: Session, redisdb: StrictRedis, nonce: Optional[int], expected: int
):
    address = "0xCFCd6565287314FF70e4C4CF309dB701C43eA5bD"
    cache_key = f"{address}_nonce"
    if nonce is not None:
        redisdb.set(cache_key, nonce)
    assert redisdb.exists(cache_key) == nonce is not None
    # get nonce from cache
    assert get_next_nonce(db, redisdb, address) == expected
    value: bytes = cast(bytes, redisdb.get(cache_key))
    # check cache
    assert int(value) == expected
    # check increase cache value
    assert get_next_nonce(db, redisdb, address) == expected + 1
