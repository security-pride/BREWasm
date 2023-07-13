import math

from BREWasm.parser.opcodes import *
from BREWasm.parser.types import TableType, Limits
from BREWasm.rewriter.section_rewriter import *

Insert = 0
Delete = 1


class IndicesFixer:
    def __init__(self, module):
        self.module = module

    def fix_call_instructions(self, expr, funcidx, type=None):
        for _, instr in enumerate(expr):
            if instr.opcode == Call and instr.args >= funcidx:
                if type is None or type == Insert:
                    instr.args += 1
                elif type == Delete:
                    instr.args -= 1
            elif instr.opcode == If:
                self.fix_call_instructions(instr.args.instrs1, funcidx)
                self.fix_call_instructions(instr.args.instrs2, funcidx)
            elif instr.opcode in [Block, Loop]:
                self.fix_call_instructions(instr.args.instrs, funcidx)
            else:
                pass

    def fix_callIndirect_instructions(self, expr, typeidx, type=None):
        for _, instr in enumerate(expr):
            if instr.opcode == CallIndirect and instr.args >= typeidx:
                if type is None or type == Insert:
                    instr.args += 1
                elif type == Delete:
                    instr.args -= 1
            elif instr.opcode == If:
                self.fix_callIndirect_instructions(instr.args.instrs1, typeidx)
                self.fix_callIndirect_instructions(instr.args.instrs2, typeidx)
            elif instr.opcode in [Block, Loop]:
                self.fix_callIndirect_instructions(instr.args.instrs, typeidx)
            else:
                pass

    def fix_global_instructions(self, expr, globalidx, type=None):
        for _, instr in enumerate(expr):
            if (instr.opcode == GlobalGet or instr.opcode == GlobalSet) and instr.args >= globalidx:
                if type is None or type == Insert:
                    instr.args += 1
                elif type == Delete:
                    instr.args -= 1
            elif instr.opcode == If:
                self.fix_global_instructions(instr.args.instrs1, globalidx)
                self.fix_global_instructions(instr.args.instrs2, globalidx)
            elif instr.opcode in [Block, Loop]:
                self.fix_global_instructions(instr.args.instrs, globalidx)
            else:
                pass

    def fix_elem_funcidx(self, elem_sec, funcidx, type=None):
        for elem in elem_sec:
            for _, func_idx in enumerate(elem.init):
                if func_idx >= funcidx:
                    if type is None or type == Insert:
                        elem.init[_] += 1
                    elif type == Delete:
                        elem.init[_] -= 1

    # def get_export_item_idx(self, export_sec, tag, idx):
    #     item_idx = -1
    #     for _, export_item in enumerate(export_sec):
    #         if export_item.desc.tag == tag and _ <= idx:
    #             item_idx += 1
    #     return item_idx

    def fix_export_funcidx(self, export_sec, funcidx, type=None):
        for export_item in export_sec:
            if export_item.desc.tag == 0 and export_item.desc.idx >= funcidx:
                if type is None or type == Insert:
                    export_item.desc.idx += 1
                elif type == Delete:
                    export_item.desc.idx -= 1

    def fix_export_globalidx(self, export_sec, globalidx, type=None):
        for export_item in export_sec:
            if export_item.desc.tag == 3 and export_item.desc.idx >= globalidx:
                if type is None or type == Insert:
                    export_item.desc.idx += 1
                elif type == Delete:
                    export_item.desc.idx += 1

    def fix_func_functypeidx(self, func_sec, functypeidx, type=None):
        for _, idx in enumerate(func_sec):
            if idx >= functypeidx:
                if type is None or type == Insert:
                    func_sec[_] += 1
                elif type == Delete:
                    func_sec[_] -= 1

    def fix_import_func_functypeidx(self, import_sec, functypeidx, type=None):
        for item in import_sec:
            if item.desc.func_type is not None and item.desc.func_type >= functypeidx:
                if type is None or type == Insert:
                    item.desc.func_type += 1
                elif type == Delete:
                    item.desc.func_type -= 1

    def fix_table_limits(self, table_sec, indirect_func_num, type=None):
        if not table_sec:
            table_sec.append(TableType(limits=Limits(1, indirect_func_num + 1, indirect_func_num + 1)))
        elif table_sec[0].limits.max != 0 and indirect_func_num > table_sec[0].limits.max:
            table_sec[0].limits.max = (indirect_func_num + 1)

    def fix_memory_limits(self, mem_sec, length, type=None):
        if mem_sec[0].max != 0 and length >= mem_sec[0].max * 65536:
            mem_sec[0].max += math.ceil((length - mem_sec[0].max) / 65536)
