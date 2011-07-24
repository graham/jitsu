from jitsu.orm.datatypes import *

import re

type_list = {
    'int':IntegerType,
    'integer':IntegerType,
    'smallint':IntegerType,
    'bool':BooleanType,
    'boolean':BooleanType,
    'varchar':VarCharType,
    'real':FloatType,
    'decimal':FloatType,
    'datetime':DateTimeType,
    'text':TextType,
    'timestamp':EpochType,
    'blob':GenericDataType

}

class ForeignKeyType(GenericDataType):
    def init(self):
        self.data_type = type_list[self.raw_type](self.raw_type, [])
        m = re.search('references (.*)\((.*)\)', self.additional)
        self.foreign_table, self.with_key = m.groups()
        self.foreign_table = self.foreign_table.strip('"')
        self.with_key = self.with_key.strip('"')
        