import pytest

from maimai_py import MaimaiClient, MaimaiClientMultithreading


def test_singleton():
    m_client1 = MaimaiClient()
    m_client2 = MaimaiClient()
    assert m_client1 is m_client2
    m_client_mt1 = MaimaiClientMultithreading(cache_ttl=114)
    m_client_mt2 = MaimaiClientMultithreading(cache_ttl=514)
    assert m_client_mt1 is not m_client_mt2
    assert m_client_mt1._cache_ttl == 114
    assert m_client_mt2._cache_ttl == 514


if __name__ == "__main__":
    pytest.main(["-q", "-x", "-p no:warnings", "-s", __file__])
