"""
Types configuration specific to GaussDB.
"""

# Copyright (C) 2020 The Psycopg Team

from .abc import AdaptContext
from ._typemod import BitTypeModifier, CharTypeModifier, NumericTypeModifier
from ._typemod import TimeTypeModifier
from ._typeinfo import TypeInfo, TypesRegistry
from ._adapters_map import AdaptersMap

# Global objects with GaussDB builtins and globally registered user types.
types = TypesRegistry()

# Global adapter maps with GaussDB types configuration
adapters = AdaptersMap(types=types)


def register_default_types(types: TypesRegistry) -> None:
    from .types.range import RangeInfo
    from .types.multirange import MultirangeInfo

    # Use tools/update_oids.py to update this data.
    for t in [
        TypeInfo('"char"', 18, 1002, typemod=CharTypeModifier),
        # autogenerated: start
        # Generated from GaussDB 505.2.0
        TypeInfo("TdigestData", 4406, 4407),
        TypeInfo("abstime", 702, 1023),
        TypeInfo("aclitem", 1033, 1034),
        TypeInfo("bit", 1560, 1561, typemod=BitTypeModifier),
        TypeInfo("blob", 88, 3201),
        TypeInfo("bool", 16, 1000, regtype="boolean"),
        TypeInfo("boolvector", 4410, 1078),
        TypeInfo("box", 603, 1020, delimiter=";"),
        TypeInfo("bpchar", 1042, 1014, regtype="character", typemod=CharTypeModifier),
        TypeInfo("bytea", 17, 1001),
        TypeInfo("byteawithoutordercol", 4403, 4405),
        TypeInfo("byteawithoutorderwithequalcol", 4402, 4404),
        TypeInfo("cid", 29, 1012),
        TypeInfo("cidr", 650, 651),
        TypeInfo("circle", 718, 719),
        TypeInfo("clob", 90, 3202),
        TypeInfo("date", 1082, 1182),
        TypeInfo("float4", 700, 1021, regtype="real"),
        TypeInfo("float8", 701, 1022, regtype="double precision"),
        TypeInfo("floatvector", 4409, 1077),
        TypeInfo("gtsvector", 3642, 3644),
        TypeInfo("hash16", 5801, 5803),
        TypeInfo("hash32", 5802, 5804),
        TypeInfo("hll", 4301, 4302),
        TypeInfo("inet", 869, 1041),
        TypeInfo("int1", 5545, 5546),
        TypeInfo("int16", 34, 1234),
        TypeInfo("int2", 21, 1005, regtype="smallint"),
        TypeInfo("int2vector", 22, 1006),
        TypeInfo("int2vector_extend", 33, 1004),
        TypeInfo("int4", 23, 1007, regtype="integer"),
        TypeInfo("int8", 20, 1016, regtype="bigint"),
        TypeInfo("interval", 1186, 1187, typemod=TimeTypeModifier),
        TypeInfo("json", 114, 199),
        TypeInfo("jsonb", 3802, 3807),
        TypeInfo("line", 628, 629),
        TypeInfo("lseg", 601, 1018),
        TypeInfo("macaddr", 829, 1040),
        TypeInfo("money", 790, 791),
        TypeInfo("name", 19, 1003),
        TypeInfo("numeric", 1700, 1231, typemod=NumericTypeModifier),
        TypeInfo("nvarchar2", 3969, 3968),
        TypeInfo("oid", 26, 1028),
        TypeInfo("oidvector", 30, 1013),
        TypeInfo("oidvector_extend", 32, 1013),
        TypeInfo("path", 602, 1019),
        TypeInfo("point", 600, 1017),
        TypeInfo("polygon", 604, 1027),
        TypeInfo("raw", 86, 87),
        TypeInfo("record", 2249, 2287),
        TypeInfo("refcursor", 1790, 2201),
        TypeInfo("regclass", 2205, 2210),
        TypeInfo("regconfig", 3734, 3735),
        TypeInfo("regdictionary", 3769, 3770),
        TypeInfo("regoper", 2203, 2208),
        TypeInfo("regoperator", 2204, 2209),
        TypeInfo("regproc", 24, 1008),
        TypeInfo("regprocedure", 2202, 2207),
        TypeInfo("regtype", 2206, 2211),
        TypeInfo("reltime", 703, 1024),
        TypeInfo("smalldatetime", 9003, 9005),
        TypeInfo("smgr", 210, 0),
        TypeInfo("text", 25, 1009),
        TypeInfo("tid", 27, 1010),
        TypeInfo(
            "time",
            1083,
            1183,
            regtype="time without time zone",
            typemod=TimeTypeModifier,
        ),
        TypeInfo(
            "timestamp",
            1114,
            1115,
            regtype="timestamp without time zone",
            typemod=TimeTypeModifier,
        ),
        TypeInfo(
            "timestamptz",
            1184,
            1185,
            regtype="timestamp with time zone",
            typemod=TimeTypeModifier,
        ),
        TypeInfo(
            "timetz",
            1266,
            1270,
            regtype="time with time zone",
            typemod=TimeTypeModifier,
        ),
        TypeInfo("tinterval", 704, 1025),
        TypeInfo("tsquery", 3615, 3645),
        TypeInfo("tsvector", 3614, 3643),
        TypeInfo("txid_snapshot", 2970, 2949),
        TypeInfo("uint1", 349, 1072),
        TypeInfo("uint2", 352, 1073),
        TypeInfo("uint4", 353, 1074),
        TypeInfo("uint8", 388, 1075),
        TypeInfo("unknown", 705, 0),
        TypeInfo("uuid", 2950, 2951),
        TypeInfo("varbit", 1562, 1563, regtype="bit varying", typemod=BitTypeModifier),
        TypeInfo(
            "varchar",
            1043,
            1015,
            regtype="character varying",
            typemod=CharTypeModifier,
        ),
        TypeInfo("xid", 28, 1011),
        TypeInfo("xid32", 31, 1029),
        TypeInfo("xml", 142, 143),
        TypeInfo("xmltype", 140, 141),
        TypeInfo("year", 1038, 1076),
        RangeInfo("daterange", 3912, 3913, subtype_oid=1082),
        RangeInfo("int4range", 3904, 3905, subtype_oid=23),
        RangeInfo("int8range", 3926, 3927, subtype_oid=20),
        RangeInfo("numrange", 3906, 3907, subtype_oid=1700),
        RangeInfo("tsrange", 3908, 3909, subtype_oid=1114),
        RangeInfo("tstzrange", 3910, 3911, subtype_oid=1184),
        MultirangeInfo("datemultirange", 4535, 6155, range_oid=3912, subtype_oid=1082),
        MultirangeInfo("int4multirange", 4451, 6150, range_oid=3904, subtype_oid=23),
        MultirangeInfo("int8multirange", 4536, 6157, range_oid=3926, subtype_oid=20),
        MultirangeInfo("nummultirange", 4532, 6151, range_oid=3906, subtype_oid=1700),
        MultirangeInfo("tsmultirange", 4533, 6152, range_oid=3908, subtype_oid=1114),
        MultirangeInfo("tstzmultirange", 4534, 6153, range_oid=3910, subtype_oid=1184),
        # autogenerated: end
    ]:
        types.add(t)


def register_default_adapters(context: AdaptContext) -> None:
    from .types import array, bool, composite, datetime, enum, json, multirange, net
    from .types import none, numeric, numpy, range, string, uuid

    array.register_default_adapters(context)
    composite.register_default_adapters(context)
    datetime.register_default_adapters(context)
    enum.register_default_adapters(context)
    json.register_default_adapters(context)
    multirange.register_default_adapters(context)
    net.register_default_adapters(context)
    none.register_default_adapters(context)
    range.register_default_adapters(context)
    string.register_default_adapters(context)
    uuid.register_default_adapters(context)

    # Both numpy Decimal and uint64 dumpers use the numeric oid, but the former
    # covers the entire numeric domain, whereas the latter only deals with
    # integers. For this reason, if we specify dumpers by oid, we want to make
    # sure to get the Decimal dumper. We enforce that by registering the
    # numeric dumpers last.
    numpy.register_default_adapters(context)
    bool.register_default_adapters(context)
    numeric.register_default_adapters(context)
