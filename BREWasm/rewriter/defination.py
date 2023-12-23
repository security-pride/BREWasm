from enum import Enum

from ..parser.module import Export as OriginExport
from ..parser.module import ExportDesc
from ..parser.module import Global as OriginGlobal
from ..parser.module import Import as OriginImport
from ..parser.module import ImportDesc
from ..parser.module import Locals
from ..parser.types import *

FunctionName = 0
GlobalName = 1
DataName = 2


class SectionName(Enum):
    CustomSec = 0
    TypeSec = 1
    ImportSec = 2
    FuncSec = 3
    TableSec = 4
    MemSec = 5
    GlobalSec = 6
    ExportSec = 7
    StartSec = 8
    ElemSec = 9
    CodeSec = 10
    DataSec = 11
    DataCountSec = 12


class ValType(Enum):
    I32 = 0x7F

    I64 = 0x7E

    F32 = 0x7D

    F64 = 0x7C


class Type:

    def __init__(self, typeidx=None, arg_types=None, ret_types=None):
        self.typeidx = typeidx

        self.arg_types = arg_types

        self.ret_types = ret_types

    def convert(self):
        param_types = []
        result_types = []
        if self.arg_types is not None:
            for arg in self.arg_types:
                match arg:
                    # I32
                    case 127:
                        param_types.append(ValTypeI32)
                    # I64
                    case 126:
                        param_types.append(ValTypeI32)
                    # F32
                    case 125:
                        param_types.append(ValTypeF32)
                    # F64
                    case 124:
                        param_types.append(ValTypeF64)

        if self.ret_types is not None:
            for arg in self.ret_types:
                match arg:
                    # I32
                    case 127:
                        result_types.append(ValTypeI32)
                    # I64
                    case 126:
                        result_types.append(ValTypeI32)
                    # F32
                    case 125:
                        result_types.append(ValTypeF32)
                    # F64
                    case 124:
                        result_types.append(ValTypeF64)

        return FuncType(FtTag, param_types, result_types)


class Import:

    def __init__(self, importidx=None, module=None, name=None, typeidx=None):
        self.importidx = importidx
        self.module = module
        self.name = name
        self.typeidx = typeidx

    def convert(self):
        return OriginImport(self.module, self.name, ImportDesc(0, func_type=self.typeidx))


class Export:

    def __init__(self, exportidx=None, name=None, funcidx=None):
        self.exportidx = exportidx
        self.name = name
        self.funcidx = funcidx

    def convert(self):
        return OriginExport(self.name, ExportDesc(0, idx=self.funcidx))


class Function:
    def __init__(self, funcidx=None, typeidx=None):
        self.funcidx = funcidx
        self.typeidx = typeidx

    def convert(self):
        return self.typeidx


class Table:
    def __init__(self, min=None, max=None):
        self.min = min
        self.max = max


class Memory:
    def __init__(self, min=None, max=None):
        self.min = min
        self.max = max


class Global:
    def __init__(self, globalidx=None, valtype=None, mut=None, val=None):
        self.globalidx = globalidx
        self.valtype = valtype
        self.mut = mut
        self.val = val

    def convert(self):
        return OriginGlobal(GlobalType(val_type=self.valtype, mut=self.mut), init=self.val)


class Element:
    def __init__(self, elemidx=None, tableidx=None, offset=None, funcidx_list=None):
        self.elemidx = elemidx
        self.tableidx = tableidx
        self.offset = offset
        self.funcidx_list = funcidx_list


class Code:
    def __init__(self, funcidx=None, local_vec=None, instr_list=None):
        self.funcidx = funcidx
        self.local_vec = local_vec
        self.instr_list = instr_list

    def convert_local_vec(self):
        locals_list = []
        for _, local in enumerate(self.local_vec):
            match local.valtype:
                case ValType.I32.value:
                    locals_list.append(Locals(1, ValType.I32.value))
                case ValType.I64.value:
                    locals_list.append(Locals(1, ValType.I64.value))
                case ValType.F32.value:
                    locals_list.append(Locals(1, ValType.F32.value))
                case ValType.F64.value:
                    locals_list.append(Locals(1, ValType.F64.value))
        return locals_list


class Local:
    def __init__(self, localidx=None, valtype=None):
        self.localidx = localidx
        self.valtype = valtype


class Start:
    def __init__(self, funcidx=None):
        self.funcidx = funcidx


class Data:
    def __init__(self, dataidx=None, offset=None, init_data=None):
        self.dataidx = dataidx
        self.offset = offset
        self.init_data = init_data


class CustomName:
    def __init__(self, name_type=None, idx=None, name=None):
        self.name_type = name_type
        self.idx = idx
        self.name = name
