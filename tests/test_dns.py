import pytest

import gaussdb
from gaussdb.conninfo import conninfo_to_dict


@pytest.mark.dns
@pytest.mark.anyio
async def test_resolve_hostaddr_async_warning(recwarn):
    import_dnspython()
    conninfo = "dbname=foo"
    params = conninfo_to_dict(conninfo)
    params = await gaussdb._dns.resolve_hostaddr_async(  # type: ignore[attr-defined]
        params
    )
    assert "resolve_hostaddr_async" in str(recwarn.pop(DeprecationWarning).message)


def import_dnspython():
    try:
        import dns.rdtypes.IN.A  # noqa: F401
    except ImportError:
        pytest.skip("dnspython package not available")

    import gaussdb._dns  # noqa: F401
