import warnings

import pytest

from maimai_py import MaimaiClient, MaimaiClientMultithreading


@pytest.mark.asyncio(scope="session")
async def test_singleton(maimai: MaimaiClient):
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        m_client2 = MaimaiClient()
        assert maimai is m_client2
    m_client_mt1 = MaimaiClientMultithreading(cache_ttl=114)
    m_client_mt2 = MaimaiClientMultithreading(cache_ttl=514)
    assert m_client_mt1 is not m_client_mt2
    assert m_client_mt1._cache_ttl == 114
    assert m_client_mt2._cache_ttl == 514


if __name__ == "__main__":
    pytest.main(["-q", "-x", "-p no:warnings", "-s", __file__])
