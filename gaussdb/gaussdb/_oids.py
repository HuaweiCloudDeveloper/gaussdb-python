"""
GaussDB known type OIDs

This is an internal module. Types are publicly exposed by
`gaussdb.gaussdb_.types`. This module is only used to know the OIDs at import
time and avoid circular import problems.
"""

# Copyright (C) 2020 The Psycopg Team

# A couple of special cases used a bit everywhere.
INVALID_OID = 0
TEXT_ARRAY_OID = 1009

# Use tools/update_oids.py to update this data.
# autogenerated: start

# Generated from GaussDB 505.2.0

TDIGESTDATA_OID = 4406
ABSTIME_OID = 702
ACLITEM_OID = 1033
BIT_OID = 1560
BLOB_OID = 88
BOOL_OID = 16
BOOLVECTOR_OID = 4410
BOX_OID = 603
BPCHAR_OID = 1042
BYTEA_OID = 17
BYTEAWITHOUTORDERCOL_OID = 4403
BYTEAWITHOUTORDERWITHEQUALCOL_OID = 4402
CHAR_OID = 18
CID_OID = 29
CIDR_OID = 650
CIRCLE_OID = 718
CLOB_OID = 90
DATE_OID = 1082
DATEMULTIRANGE_OID = 4535
DATERANGE_OID = 3912
FLOAT4_OID = 700
FLOAT8_OID = 701
FLOATVECTOR_OID = 4409
GTSVECTOR_OID = 3642
HASH16_OID = 5801
HASH32_OID = 5802
HLL_OID = 4301
INET_OID = 869
INT1_OID = 5545
INT16_OID = 34
INT2_OID = 21
INT2VECTOR_OID = 22
INT2VECTOR_EXTEND_OID = 33
INT4_OID = 23
INT4MULTIRANGE_OID = 4451
INT4RANGE_OID = 3904
INT8_OID = 20
INT8MULTIRANGE_OID = 4536
INT8RANGE_OID = 3926
INTERVAL_OID = 1186
JSON_OID = 114
JSONB_OID = 3802
JSONPATH_OID = 4072
LINE_OID = 628
LSEG_OID = 601
MACADDR_OID = 829
MACADDR8_OID = 774
MONEY_OID = 790
NAME_OID = 19
NUMERIC_OID = 1700
NUMMULTIRANGE_OID = 4532
NUMRANGE_OID = 3906
NVARCHAR2_OID = 3969
OID_OID = 26
OIDVECTOR_OID = 30
OIDVECTOR_EXTEND_OID = 32
PATH_OID = 602
PG_LSN_OID = 3220
POINT_OID = 600
POLYGON_OID = 604
RAW_OID = 86
RECORD_OID = 2249
REFCURSOR_OID = 1790
REGCLASS_OID = 2205
REGCOLLATION_OID = 4191
REGCONFIG_OID = 3734
REGDICTIONARY_OID = 3769
REGNAMESPACE_OID = 4089
REGOPER_OID = 2203
REGOPERATOR_OID = 2204
REGPROC_OID = 24
REGPROCEDURE_OID = 2202
REGROLE_OID = 4096
REGTYPE_OID = 2206
RELTIME_OID = 703
SMALLDATETIME_OID = 9003
SMGR_OID = 210
TEXT_OID = 25
TID_OID = 27
TIME_OID = 1083
TIMESTAMP_OID = 1114
TIMESTAMPTZ_OID = 1184
TIMETZ_OID = 1266
TSMULTIRANGE_OID = 4533
TSQUERY_OID = 3615
TSRANGE_OID = 3908
TSTZMULTIRANGE_OID = 4534
TSTZRANGE_OID = 3910
TSVECTOR_OID = 3614
TXID_SNAPSHOT_OID = 2970
UINT1_OID = 349
UINT2_OID = 352
UINT4_OID = 353
UINT8_OID = 388
UNKNOWN_OID = 705
UUID_OID = 2950
VARBIT_OID = 1562
VARCHAR_OID = 1043
XID_OID = 28
XID8_OID = 5069
XML_OID = 142
XMLTYPE_OID = 140
YEAR_OID = 1038

# autogenerated: end
