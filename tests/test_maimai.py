from maimai_py import MaimaiClient, MaimaiClientMultithreading


def test_singleton():
    m_client1 = MaimaiClient()
    m_client2 = MaimaiClient()
    assert m_client1 is m_client2
    m_client_mt1 = MaimaiClientMultithreading()
    m_client_mt2 = MaimaiClientMultithreading()
    assert m_client_mt1 is not m_client_mt2
