import os
import struct

from leb128 import LEB128U, LEB128S
from BREWasm.parser import reader
from BREWasm.parser.instruction import Instruction
from BREWasm.parser.module import *
from BREWasm.parser.opcodes import *
from BREWasm.parser.types import val_type_to_str, GlobalType


class ModifyBinary:

    def __init__(self, module: Module, path: str):
        if module is None:
            module, err = reader.decode_file(path)
            if err is not None:
                print(err.args)
                print("=================================")
                raise Exception("Failed to read the wasm file!  " + str(err.args))

            self.module = module
            self.module.path = path

            self.func_name = []
            for custom in self.module.custom_secs:
                if custom.name == "name":
                    if custom.name_data.funcNameSubSec is not None:

                        for func_name_item in custom.name_data.funcNameSubSec[self.get_import_func_num():]:
                            self.func_name.append(func_name_item.name)
        else:
            self.module = module
            self.module.path = path

    def get_import_func_num(self):

        num = 0
        for _, import_item in enumerate(self.module.import_sec):
            if import_item.desc.func_type != None:
                num += 1

        return num

    def emit_binary(self, path):

        if os.path.isfile(path):
            if not os.path.samefile(self.module.path, path):
                os.remove(path)

        with open(path, "wb+") as f:

            magic_version_number = struct.pack("II", self.module.magic, self.module.version)
            f.write(magic_version_number)


            if self.module.type_sec:
                self.emit_type_section(self.module.type_sec, f)
            if self.module.import_sec:
                self.emit_import_section(self.module.import_sec, f)
            if self.module.func_sec:
                self.emit_func_section(self.module.func_sec, f)
            if self.module.table_sec:
                self.emit_table_section(self.module.table_sec, f)
            if self.module.mem_sec:
                self.emit_memory_section(self.module.mem_sec, f)
            if self.module.global_sec:
                self.emit_global_section(self.module.global_sec, f)
            if self.module.export_sec:
                self.emit_export_section(self.module.export_sec, f)
            if self.module.start_sec:
                self.emit_start_section(self.module.start_sec, f)
            if self.module.elem_sec:
                self.emit_elem_section(self.module.elem_sec, f)
            if self.module.code_sec:
                self.emit_code_section(self.module.code_sec, f)
            if self.module.data_sec:
                self.emit_data_section(self.module.data_sec, f)
            if self.module.datacount_sec:
                self.emit_datacount_section(self.module.datacount_sec, f)
            if self.module.custom_secs:
                self.emit_custom_section(self.module.custom_secs, f)


    def print_function(self, func_id):

        type_id = self.module.func_sec[func_id]
        if len(self.func_name) == 0:
            print("(func %d (type %d) " % (func_id, type_id), end="")
        else:

            print("(func %s (type %d) " % (self.func_name[func_id], type_id), end="")
        param_types_str = ""
        result_types_str = ""
        print("=======" + str(type_id))
        if self.module.type_sec[type_id].param_types:
            for i in self.module.type_sec[type_id].param_types:
                param_types_str += (val_type_to_str(i) + " ")
        if self.module.type_sec[type_id].result_types:
            for i in self.module.type_sec[type_id].result_types:
                result_types_str += (val_type_to_str(i) + " ")

        print("(param %s)" % param_types_str, end="")
        print("(result %s)" % result_types_str)

        if self.module.code_sec[func_id].locals is not None:
            print("(locals", end=" ")
            for local in self.module.code_sec[func_id].locals:
                print((val_type_to_str(local.type) + " ") * local.n, end="")
            print(")")
        self.dump_expr("    ", self.module.code_sec[func_id].expr)
        print(")")


    def dump_expr(self, indentation, expr):

        for _, instr in enumerate(expr):
            if instr.opcode in [Block, Loop]:
                args = instr.args
                bt = self.module.get_block_type(args.bt)
                print("%s%s %s" % (indentation, instr.get_opname(), bt))
                self.dump_expr(indentation + "  ", args.instrs)
                print("%s%s" % (indentation, "end"))
            elif instr.opcode == If:
                args = instr.args
                bt = self.module.get_block_type(args.bt)
                print("%s%s %s" % (indentation, "if", bt))
                self.dump_expr(indentation + "  ", args.instrs1)
                print("%s%s" % (indentation, "else"))
                self.dump_expr(indentation + "  ", args.instrs2)
                print("%s%s" % (indentation, "end"))
            else:
                if instr.args is not None:
                    if 0x36 <= instr.opcode <= 0x3E or 0x28 <= instr.opcode <= 0x35:
                        print("{}{} align={} offset={} ".format(indentation, instr.get_opname(), instr.args.align,
                                                                instr.args.offset))
                    else:
                        print("{}{} {}".format(indentation, instr.get_opname(), instr.args))
                elif instr.args is None:
                    print("{}{}".format(indentation, instr.get_opname()))



    def emit_custom_section(self, custom_vec: list, fp):

        for _, custom in enumerate(custom_vec):
            if custom.name == "name":
                name_section_bytes = bytes()
                name_section_bytes += LEB128U.encode(len(custom.name))
                name_section_bytes += bytes(custom.name, encoding="utf-8")
                if custom.name_data.moduleNameSubSec != None:
                    name_section_bytes += bytes([0x00])
                    name_section_bytes += LEB128U.encode(len(custom.name_data.moduleNameSubSec))
                    name_section_bytes += custom.name_data.moduleNameSubSec
                if custom.name_data.funcNameSubSec != []:

                    funcname_bytes = bytes()
                    funcname_bytes += LEB128U.encode(len(custom.name_data.funcNameSubSec))
                    for funcname in custom.name_data.funcNameSubSec:
                        funcname_bytes += LEB128U.encode(funcname.idx)
                        funcname_bytes += LEB128U.encode(len(funcname.name))
                        funcname_bytes += bytes(funcname.name, encoding="utf-8")
                    name_section_bytes += (bytes([0x01]) + LEB128U.encode(len(funcname_bytes))) + funcname_bytes

                if custom.name_data.localNameSubSec != None:
                    name_section_bytes += bytes([0x02])
                    name_section_bytes += LEB128U.encode(len(custom.name_data.localNameSubSec))
                    name_section_bytes += custom.name_data.localNameSubSec
                if custom.name_data.labelsNameSubSec != None:
                    name_section_bytes += bytes([0x03])
                    name_section_bytes += LEB128U.encode(len(custom.name_data.labelsNameSubSec))
                    name_section_bytes += custom.name_data.labelsNameSubSec
                if custom.name_data.typeNameSubSec != None:
                    name_section_bytes += bytes([0x04])
                    name_section_bytes += LEB128U.encode(len(custom.name_data.typeNameSubSec))
                    name_section_bytes += custom.name_data.typeNameSubSec
                if custom.name_data.tableNameSubSec != []:
                    tablename_bytes = bytes()
                    tablename_bytes += LEB128U.encode(len(custom.name_data.tableNameSubSec))
                    for tablename in custom.name_data.tableNameSubSec:
                        tablename_bytes += LEB128U.encode(tablename.idx)
                        tablename_bytes += LEB128U.encode(len(tablename.name))
                        tablename_bytes += bytes(tablename.name, encoding="utf-8")
                    name_section_bytes += (bytes([0x05]) + LEB128U.encode(len(tablename_bytes))) + tablename_bytes
                if custom.name_data.memoryNameSubSec != None:
                    name_section_bytes += bytes([0x06])
                    name_section_bytes += LEB128U.encode(len(custom.name_data.memoryNameSubSec))
                    name_section_bytes += custom.name_data.memoryNameSubSec
                if custom.name_data.globalNameSubSec != []:
                    globalname_bytes = bytes()
                    globalname_bytes += LEB128U.encode(len(custom.name_data.globalNameSubSec))
                    for globalname in custom.name_data.globalNameSubSec:
                        globalname_bytes += LEB128U.encode(globalname.idx)
                        globalname_bytes += LEB128U.encode(len(globalname.name))
                        globalname_bytes += bytes(globalname.name, encoding="utf-8")
                    name_section_bytes += (bytes([0x07]) + LEB128U.encode(len(globalname_bytes))) + globalname_bytes
                if custom.name_data.elemNameSubSec != None:
                    name_section_bytes += bytes([0x08])
                    name_section_bytes += LEB128U.encode(len(custom.name_data.elemNameSubSec))
                    name_section_bytes += custom.name_data.elemNameSubSec
                if custom.name_data.dataNameSubSec != []:
                    dataname_bytes = bytes()
                    dataname_bytes += LEB128U.encode(len(custom.name_data.dataNameSubSec))
                    for dataname in custom.name_data.dataNameSubSec:
                        dataname_bytes += LEB128U.encode(dataname.idx)
                        dataname_bytes += LEB128U.encode(len(dataname.name))
                        dataname_bytes += bytes(dataname.name, encoding="utf-8")
                    name_section_bytes += (bytes([0x09]) + LEB128U.encode(len(dataname_bytes))) + dataname_bytes


                name_section_bytes = bytes([0x00]) + LEB128U.encode(len(name_section_bytes)) + name_section_bytes

                fp.write(name_section_bytes)
            else:
                custom_section_bytes = bytes()
                custom_section_bytes += custom.custom_sec_data

                custom_section_bytes = bytes([0x00]) + LEB128U.encode(
                    len(custom_section_bytes)) + custom_section_bytes
                fp.write(custom_section_bytes)

    def emit_start_section(self, start_funcid, fp):
        start_funcid_bytes = LEB128U.encode(start_funcid)
        start_section_bytes = bytes([0x08]) + LEB128U.encode(len(start_funcid_bytes)) + start_funcid_bytes

        fp.write(start_section_bytes)


    def emit_datacount_section(self, datacount: int, fp):
        if datacount != None:
            datacount_bytes = LEB128U.encode(datacount)
            datacount_section_bytes = bytes([SecDataCountID]) + LEB128U.encode(len(datacount_bytes)) + datacount_bytes

            fp.write(datacount_section_bytes)

    def emit_import_section(self, import_vec: list, fp):

        import_vec_len = len(import_vec)
        import_vec_len_bytes = LEB128U.encode(import_vec_len)
        import_vec_bytes = bytes()
        import_vec_bytes += import_vec_len_bytes
        if import_vec == []:
            return
        for i in import_vec:
            import_vec_bytes += LEB128U.encode(len(i.module))
            import_vec_bytes += bytes(i.module, encoding="utf-8")
            import_vec_bytes += LEB128U.encode(len(i.name))
            import_vec_bytes += bytes(i.name, encoding="utf-8")
            import_vec_bytes += LEB128U.encode(i.desc.tag)
            if i.desc.func_type is not None:
                import_vec_bytes += LEB128U.encode(i.desc.func_type)
            elif i.desc.table is not None:
                import_vec_bytes += self.write_table_type(i.desc.table)
            elif i.desc.mem is not None:
                import_vec_bytes += self.write_limits(i.desc.mem)
            elif i.desc.global_type is not None:
                import_vec_bytes += self.write_global_type(i.desc.global_type)
        import_section_bytes = bytes([0x02]) + LEB128U.encode(len(import_vec_bytes)) + import_vec_bytes

        fp.write(import_section_bytes)

    def emit_export_section(self, export_vec: list, fp):
        export_vec_len = len(export_vec)
        export_vec_len_bytes = LEB128U.encode(export_vec_len)
        export_vec_bytes = bytes()
        export_vec_bytes += export_vec_len_bytes
        if export_vec == []:
            return
        for export_item in export_vec:
            export_vec_bytes += LEB128U.encode(len(export_item.name))
            export_vec_bytes += bytes(export_item.name, encoding="utf-8")
            export_vec_bytes += LEB128U.encode(export_item.desc.tag)
            export_vec_bytes += LEB128U.encode(export_item.desc.idx)

        export_section_bytes = bytes([0x07]) + LEB128U.encode(len(export_vec_bytes)) + export_vec_bytes

        fp.write(export_section_bytes)

    def emit_memory_section(self, memory_vec: list, fp):
        memory_vec_len = len(memory_vec)
        memory_vec_len_bytes = LEB128U.encode(memory_vec_len)
        memory_vec_bytes = bytes()
        memory_vec_bytes += memory_vec_len_bytes
        if memory_vec == []:
            return
        for memory_item in memory_vec:
            memory_item_bytes = bytes()
            memory_item_bytes += bytes([memory_item.tag])
            memory_item_bytes += LEB128U.encode(memory_item.min)
            if memory_item.max != 0:
                memory_item_bytes += LEB128U.encode(memory_item.max)
            memory_vec_bytes += memory_item_bytes

        memroy_section_bytes = bytes([SecMemID]) + LEB128U.encode(len(memory_vec_bytes)) + memory_vec_bytes

        fp.write(memroy_section_bytes)

    def emit_data_section(self, data_vec: list, fp):
        data_vec_len = len(data_vec)
        data_vec_len_bytes = LEB128U.encode(data_vec_len)
        data_vec_bytes = bytes()
        data_vec_bytes += data_vec_len_bytes
        if not data_vec:
            return
        for data_item in data_vec:
            data_item_bytes = bytes()
            data_item_bytes += LEB128U.encode(data_item.mem)
            data_item_bytes += self.write_expr(data_item.offset)
            data_item_bytes += LEB128U.encode(len(data_item.init))
            data_item_bytes += data_item.init

            data_vec_bytes += data_item_bytes

        data_section_bytes = bytes([SecDataID]) + LEB128U.encode(len(data_vec_bytes)) + data_vec_bytes

        fp.write(data_section_bytes)

    def emit_elem_section(self, elem_vec: list, fp):

        elem_vec_len = len(elem_vec)
        elem_vec_len_bytes = LEB128U.encode(elem_vec_len)
        elem_vec_bytes = bytes()
        elem_vec_bytes += elem_vec_len_bytes
        if elem_vec == []:
            return
        for elem in elem_vec:
            elem_vec_bytes += LEB128U.encode(elem.table)
            elem_vec_bytes += self.write_expr(elem.offset)
            elem_vec_bytes += LEB128U.encode(len(elem.init))
            for func_idx in elem.init:
                elem_vec_bytes += LEB128U.encode(func_idx)
        elem_section_bytes = bytes([SecElemID]) + LEB128U.encode(len(elem_vec_bytes)) + elem_vec_bytes

        fp.write(elem_section_bytes)

    def emit_type_section(self, functype_vec: list, fp):

        functype_vec_len = len(functype_vec)
        functype_vec_len_bytes = LEB128U.encode(functype_vec_len)
        functype_vec_bytes = bytes()
        functype_vec_bytes += functype_vec_len_bytes
        if functype_vec == []:
            return
        for functype in functype_vec:
            functype_bytes = bytes()
            functype_bytes += bytes([0x60])
            functype_bytes += self.write_val_types(functype.param_types)
            functype_bytes += self.write_val_types(functype.result_types)
            functype_vec_bytes += functype_bytes
        type_section_bytes = bytes([0x01]) + LEB128U.encode(len(functype_vec_bytes)) + functype_vec_bytes

        fp.write(type_section_bytes)

    def emit_global_section(self, global_vec: list, fp):

        global_vec_len = len(global_vec)
        global_vec_len_bytes = LEB128U.encode(global_vec_len)
        global_vec_bytes = bytes()
        global_vec_bytes += global_vec_len_bytes
        if global_vec == []:
            return
        for global_item in global_vec:
            global_bytes = bytes()
            global_bytes += self.write_global(global_item)
            global_vec_bytes += global_bytes

        global_section_bytes = bytes([0x06]) + LEB128U.encode(len(global_vec_bytes)) + global_vec_bytes

        fp.write(global_section_bytes)

    def emit_func_section(self, type_vec, fp):

        type_vec_len = len(type_vec)
        type_vec_len_bytes = LEB128U.encode(type_vec_len)
        type_vec_bytes = bytes()
        type_vec_bytes += type_vec_len_bytes
        if type_vec == []:
            return
        for type_item in type_vec:
            type_vec_bytes += LEB128U.encode(type_item)
        func_section_bytes = bytes([0x03]) + LEB128U.encode(len(type_vec_bytes)) + type_vec_bytes

        fp.write(func_section_bytes)

    def emit_code_section(self, code_vec: list, fp):

        code_vec_len = len(code_vec)
        code_vec_len_bytes = LEB128U.encode(code_vec_len)
        code_vec_bytes = bytes()
        code_vec_bytes += code_vec_len_bytes
        if code_vec == []:
            return
        for code in code_vec:
            code_bytes = bytes()
            locals_vec_len = len(code.locals)
            locals_vec_len_bytes = LEB128U.encode(locals_vec_len)
            locals_vec_bytes = bytes()
            expr_bytes = bytes()

            for local in code.locals:
                local_count = local.n
                local_type = local.type
                locals_vec_bytes += LEB128U.encode(local_count)
                locals_vec_bytes += bytes([local_type])

            expr_bytes += self.write_expr(code.expr)
            code_bytes += (locals_vec_len_bytes + locals_vec_bytes + expr_bytes)
            code_vec_bytes += LEB128U.encode(len(code_bytes)) + code_bytes
        code_section_bytes = bytes([0x0A]) + LEB128U.encode(len(code_vec_bytes)) + code_vec_bytes

        fp.write(code_section_bytes)

    def emit_table_section(self, table_vec: list, fp):

        table_vec_len = len(table_vec)
        table_vec_len_bytes = LEB128U.encode(table_vec_len)
        table_vec_bytes = bytes()
        table_vec_bytes += table_vec_len_bytes
        if table_vec == []:
            return
        for table_type in table_vec:
            table_type_bytes = bytes()
            table_type_bytes += bytes([table_type.elem_type])
            table_type_bytes += bytes([table_type.limits.tag])
            table_type_bytes += LEB128U.encode(table_type.limits.min)
            if 0 != table_type.limits.max:
                table_type_bytes += LEB128U.encode(table_type.limits.max)
            table_vec_bytes += table_type_bytes

        table_section_bytes = bytes([0x04]) + LEB128U.encode(len(table_vec_bytes)) + table_vec_bytes

        fp.write(table_section_bytes)

    def write_expr(self, expr: list):

        instructions_bytes = self.write_instructions(expr)
        expr_bytes = instructions_bytes + bytes([0x0b])

        return expr_bytes

    def write_instructions(self, expr: list):

        instructions_bytes = bytes()
        for index in range(len(expr)):
            instructions_bytes += self.write_instruction(expr[index])

        return instructions_bytes

    def write_instruction(self, instr: Instruction):

        binary_data = bytes()

        if instr.opcode < 0xFC:
            binary_data += bytes([instr.opcode])


        elif instr.opcode <= 0xFD7F:
            binary_data += instr.opcode.to_bytes(2, 'big')


        elif instr.opcode <= 0xFDFF01:
            binary_data += instr.opcode.to_bytes(3, 'big')

        else:
            raise Exception("Invalid opcode: 0x%02x" % instr.opcode)

        args_bytes = self.write_args(instr)
        if args_bytes != None:
            binary_data += args_bytes

        return binary_data

    def write_args(self, instr):

        opcode = instr.opcode
        if opcode in [Block, Loop]:
            return self.write_block_args(instr)
        elif opcode == If:
            return self.write_if_args(instr)
        elif opcode in [Br, BrIf]:
            return LEB128U.encode(instr.args)
        elif opcode == BrTable:
            return self.write_br_table_args(instr)
        elif opcode == Call:
            return LEB128U.encode(instr.args)
        elif opcode == CallIndirect:
            return self.write_call_indirect_args(instr)
        elif opcode in [LocalGet, LocalSet, LocalTee]:
            return LEB128U.encode(instr.args)
        elif opcode in [GlobalGet, GlobalSet]:
            return LEB128U.encode(instr.args)
        elif opcode in [MemorySize, MemoryGrow]:
            return bytes([0x00])
        elif opcode == I32Const:
            return LEB128S.encode(instr.args)
        elif opcode == I64Const:
            return LEB128S.encode(instr.args)
        elif opcode == F32Const:
            return struct.pack('<f', instr.args)
        elif opcode == F64Const:
            return struct.pack('<d', instr.args)
        elif opcode == V128Const:
            return instr.args.to_bytes(16, 'little')
        elif opcode == I8x16Shuffle:
            return instr.args.to_bytes(16, 'little')
        elif I8x16ExtractLaneS <= opcode <= F64x2ReplaceLane:
            return bytes([instr.args])
        elif opcode in [RefNull, RefFunc]:
            return LEB128U.encode(instr.args)
        elif opcode in [MemoryInit, DataDrop, ElemDrop, TableGrow, TableSize, TableFill]:
            return LEB128U.encode(instr.args)
        elif opcode in [TableInit, TableCopy]:
            x = LEB128U.encode(instr.args.x)
            y = LEB128U.encode(instr.args.y)
            return x + y
        elif V128Load <= opcode <= V128Store or opcode in [V128Load32Zero, V128Load64Zero]:
            return self.write_mem_arg(instr)
        elif V128Load8Lane <= opcode <= V128Store64Lane:
            return self.write_mem_lane_arg(instr)
        elif I32Load <= instr.opcode <= I64Store32:
            return self.write_mem_arg(instr)
        else:
            return None

    def write_block_args(self, instr):

        args_bytes = bytes()
        args_bytes += LEB128S.encode(instr.args.bt)
        args_bytes += self.write_instructions(instr.args.instrs)
        args_bytes += bytes([0x0b])

        return args_bytes

    def write_if_args(self, instr):

        args_bytes = bytes()
        args_bytes += LEB128S.encode(instr.args.bt)
        args_bytes += self.write_instructions(instr.args.instrs1)
        if instr.args.instrs2:
            args_bytes += bytes([0x05])
            args_bytes += self.write_instructions(instr.args.instrs2)
            args_bytes += bytes([0x0b])
        else:
            args_bytes += bytes([0x0b])

        return args_bytes

    @staticmethod
    def write_br_table_args(instr):

        args_bytes = bytes()
        args_bytes += LEB128U.encode(len(instr.args.labels))
        for label in instr.args.labels:
            args_bytes += LEB128U.encode(label)
        args_bytes += LEB128U.encode(instr.args.default)

        return args_bytes

    @staticmethod
    def write_call_indirect_args(instr):

        args_bytes = bytes()
        args_bytes += LEB128U.encode(instr.args)
        args_bytes += bytes([0x00])

        return args_bytes

    @staticmethod
    def write_mem_arg(instr):

        args_bytes = bytes()
        args_bytes += LEB128U.encode(instr.args.align)
        args_bytes += LEB128U.encode(instr.args.offset)

        return args_bytes

    @staticmethod
    def write_mem_lane_arg(instr):

        args_bytes = bytes()
        args_bytes += LEB128U.encode(instr.args.mem_arg.align)
        args_bytes += LEB128U.encode(instr.args.mem_arg.offset)
        args_bytes += LEB128U.encode(instr.args.laneidx)

        return args_bytes

    @staticmethod
    def write_val_types(val_types):

        val_types_bytes = bytes()
        val_types_bytes += LEB128U.encode(len(val_types))
        for val in val_types:
            val_types_bytes += bytes([val])

        return val_types_bytes

    @staticmethod
    def write_global_type(global_type):

        global_type_bytes = bytes()
        global_type_bytes += bytes([global_type.val_type])
        global_type_bytes += bytes([global_type.mut])
        return global_type_bytes

    @staticmethod
    def write_limits(mem):

        mem_bytes = bytes()
        mem_bytes += bytes([mem.tag])
        mem_bytes += LEB128U.encode(mem.min)
        if mem.tag == 1:
            mem_bytes += LEB128U.encode(mem.max)
        return mem_bytes

    @staticmethod
    def write_table_type(table_type):

        table_type_bytes = bytes()
        table_type_bytes += bytes([table_type.elem_type])
        table_type_bytes += bytes([table_type.limits.tag])
        if table_type.limits.min != 0:
            table_type_bytes += LEB128U.encode(table_type.limits.min)
        if table_type.limits.max != 0:
            table_type_bytes += LEB128U.encode(table_type.limits.max)
        return table_type_bytes

    def write_global(self, global_item):
        global_bytes = bytes()
        global_bytes += self.write_global_type(global_item.type)
        global_bytes += self.write_expr(global_item.init)
        return global_bytes



def get_functype_idx(module, functype):
    functype_id = None
    for _, i in enumerate(module.type_sec):
        if i.equal(functype) is True:
            functype_id = _
    return functype_id
