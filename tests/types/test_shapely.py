import pytest

import gaussdb
from gaussdb.pq import Format
from gaussdb.adapt import PyFormat
from gaussdb.types import TypeInfo

pytest.importorskip("shapely")

from shapely.geometry import MultiPolygon, Point, Polygon

from gaussdb.types.shapely import register_shapely, shapely_version

if shapely_version >= (2, 0):
    from shapely import get_srid, set_srid
else:

    def set_srid(obj, srid):  # type: ignore[no-redef]
        return obj

    def get_srid(obj):  # type: ignore[no-redef]
        raise NotImplementedError


pytestmark = [
    pytest.mark.postgis,
    pytest.mark.crdb("skip"),
]

SAMPLE_POINT = Point(1.2, 3.4)
SAMPLE_POLYGON = Polygon([(0, 0), (1, 1), (1, 0)])
SAMPLE_POLYGON_4326 = set_srid(SAMPLE_POLYGON, 4326)

# real example, with CRS and "holes"
MULTIPOLYGON_GEOJSON = """
{
   "type":"MultiPolygon",
   "crs":{
      "type":"name",
      "properties":{
         "name":"EPSG:3857"
      }
   },
   "coordinates":[
      [
         [
            [89574.61111389, 6894228.638802719],
            [89576.815239808, 6894208.60747024],
            [89576.904295401, 6894207.820852726],
            [89577.99522641, 6894208.022080451],
            [89577.961830563, 6894209.229446936],
            [89589.227363031, 6894210.601454523],
            [89594.615226386, 6894161.849595264],
            [89600.314784314, 6894111.37846976],
            [89651.187791607, 6894116.774968589],
            [89648.49385993, 6894140.226914071],
            [89642.92788539, 6894193.423936413],
            [89639.721884055, 6894224.08372821],
            [89589.283022777, 6894218.431048969],
            [89588.192091767, 6894230.248628867],
            [89574.61111389, 6894228.638802719]
         ],
         [
            [89610.344670435, 6894182.466199101],
            [89625.985058891, 6894184.258949757],
            [89629.547282597, 6894153.270030369],
            [89613.918026089, 6894151.458993318],
            [89610.344670435, 6894182.466199101]
         ]
      ]
   ]
}"""

SAMPLE_POINT_GEOJSON = '{"type":"Point","coordinates":[1.2, 3.4]}'


@pytest.fixture
def shapely_conn(conn, svcconn):
    try:
        with svcconn.transaction():
            svcconn.execute("create extension if not exists postgis")
    except gaussdb.Error as e:
        pytest.skip(f"can't create extension postgis: {e}")

    info = TypeInfo.fetch(conn, "geometry")
    assert info
    register_shapely(info, conn)
    return conn


def test_no_adapter(conn):
    point = Point(1.2, 3.4)
    with pytest.raises(gaussdb.ProgrammingError, match="cannot adapt type 'Point'"):
        conn.execute("SELECT pg_typeof(%s)", [point]).fetchone()[0]


def test_no_info_error(conn):
    from gaussdb.types.shapely import register_shapely

    with pytest.raises(TypeError, match="postgis.*extension"):
        register_shapely(None, conn)  # type: ignore[arg-type]


@pytest.mark.parametrize("fmt_in", PyFormat)
@pytest.mark.parametrize("obj", ["SAMPLE_POINT", "SAMPLE_POLYGON"])
def test_with_adapter(shapely_conn, obj, fmt_in):
    obj = globals()[obj]
    with shapely_conn.cursor() as cur:
        cur.execute(f"SELECT pg_typeof(%{fmt_in.value})", [obj])
        assert cur.fetchone()[0] == "geometry"


@pytest.mark.parametrize("fmt_in", PyFormat)
@pytest.mark.parametrize("fmt_out", Format)
@pytest.mark.parametrize(
    "obj, srid",
    [("SAMPLE_POINT", 0), ("SAMPLE_POLYGON", 0), ("SAMPLE_POLYGON_4326", 4326)],
)
def test_write_read_shape(shapely_conn, fmt_in, fmt_out, obj, srid):
    obj = globals()[obj]
    with shapely_conn.cursor(binary=fmt_out) as cur:
        cur.execute("drop table if exists sample_geoms")
        cur.execute("create table sample_geoms(id SERIAL PRIMARY KEY, geom geometry)")
        cur.execute(f"insert into sample_geoms(geom) VALUES(%{fmt_in.value})", (obj,))
        cur.execute("select geom from sample_geoms")
        result = cur.fetchone()[0]
        assert result == obj
        if shapely_version >= (2, 0):
            assert get_srid(result) == srid


@pytest.mark.parametrize("fmt_out", Format)
def test_match_geojson(shapely_conn, fmt_out):
    with shapely_conn.cursor(binary=fmt_out) as cur:
        cur.execute("select ST_GeomFromGeoJSON(%s)", (SAMPLE_POINT_GEOJSON,))
        result = cur.fetchone()[0]
        # clone the coordinates to have a list instead of a shapely wrapper
        assert result.coords[:] == SAMPLE_POINT.coords[:]

        cur.execute("select ST_GeomFromGeoJSON(%s)", (MULTIPOLYGON_GEOJSON,))
        result = cur.fetchone()[0]
        assert isinstance(result, MultiPolygon)
