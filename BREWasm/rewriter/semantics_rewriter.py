from BREWasm.parser.instruction import Instruction
from BREWasm.rewriter.indices_fixer import IndicesFixer
from BREWasm.rewriter.section_rewriter import *


class SemanticsRewriter:

    class GlobalVariable:
        def __init__(self, module):
            self.module = module

        def insert_global_variable(self, idx, global_type, init_value):
            global_rewriter = SectionRewriter(self.module, globalsec=self.module.global_sec)
            global_rewriter.insert(Global(globalidx=idx), Global(valtype=global_type, val=init_value))

        def append_global_variable(self, global_type, init_value):
            global_rewriter = SectionRewriter(self.module, globalsec=self.module.global_sec)
            global_rewriter.insert(None, inserted_item=Global(valtype=global_type, val=init_value))

        def modify_global_variable(self, idx, global_type, init_value):
            global_rewriter = SectionRewriter(self.module, globalsec=self.module.global_sec)
            global_rewriter.update(Global(globalidx=idx), Global(valtype=global_type, val=init_value))

        def delete_global_variable(self, idx=None, global_type=None, init_value=None):
            if idx is not None:
                global_rewriter = SectionRewriter(self.module, globalsec=self.module.global_sec)
                global_rewriter.delete(Global(globalidx=idx))
                return
            if global_type is not None and init_value is not None:
                global_rewriter = SectionRewriter(self.module, globalsec=self.module.global_sec)
                global_variable = global_rewriter.select(Global(valtype=global_type, val=init_value))
                global_rewriter.delete(global_variable[0].globalidx)

    class ImportExport:
        def __init__(self, module):
            self.module = module

        def insert_import_function(self, idx, module_name, func_name, params_type, results_type):

            type_rewriter = SectionRewriter(self.module, typesec=self.module.type_sec)
            result = type_rewriter.select(Type(arg_types=params_type, ret_types=results_type))
            if result == []:
                type_rewriter.insert(None, inserted_item=Type(arg_types=params_type, ret_types=results_type))
                typeidx = type_rewriter.select(Type())[-1].typeidx
            else:
                typeidx = result[0].typeidx

            import_rewriter = SectionRewriter(self.module, importsec=self.module.import_sec)
            import_rewriter.insert(Import(importidx=idx),
                                   Import(module=module_name, name=func_name, typeidx=typeidx))

        def delete_import_function(self, idx=None, module_name=None, func_name=None):

            if idx is not None:
                import_rewriter = SectionRewriter(self.module, importsec=self.module.import_sec)
                import_rewriter.delete(Import(importidx=idx))
                return
            if module_name is not None and func_name is not None:
                import_rewriter = SectionRewriter(self.module, importsec=self.module.import_sec)
                import_function = import_rewriter.select(Import(module=module_name, name=func_name))
                import_rewriter.delete(import_function[0].importidx)

        def modify_import_function(self, idx, module_name, func_name, params_type, results_type):
            type_rewriter = SectionRewriter(self.module, typesec=self.module.type_sec)
            result = type_rewriter.select(Type(arg_types=params_type, ret_types=results_type))
            if result == []:
                type_rewriter.insert(None, inserted_item=Type(arg_types=params_type, ret_types=results_type))
                typeidx = type_rewriter.select(Type())[-1].typeidx
            else:
                typeidx = result[0].typeidx

            import_rewriter = SectionRewriter(self.module, importsec=self.module.import_sec)
            import_rewriter.update(Import(importidx=idx), Import(module=module_name, name=func_name, typeidx=typeidx))

        def append_import_function(self, module_name, func_name, params_type, results_type):
            type_rewriter = SectionRewriter(self.module, typesec=self.module.type_sec)
            result = type_rewriter.select(Type(arg_types=params_type, ret_types=results_type))
            if result == []:
                type_rewriter.insert(None, inserted_item=Type(arg_types=params_type, ret_types=results_type))
                typeidx = type_rewriter.select(Type())[-1].typeidx
            else:
                typeidx = result[0].typeidx

            import_rewriter = SectionRewriter(self.module, importsec=self.module.import_sec)
            import_rewriter.insert(None, inserted_item=Import(module=module_name, name=func_name, typeidx=typeidx))

        def insert_export_function(self, idx, func_name, funcidx):

            export_rewriter = SectionRewriter(self.module, exportsec=self.module.export_sec)
            export_rewriter.insert(Export(exportidx=idx), Export(name=func_name, funcidx=funcidx))

        def modify_export_function(self, idx, func_name, funcidx):

            export_rewriter = SectionRewriter(self.module, exportsec=self.module.export_sec)
            export_rewriter.update(Export(exportidx=idx), Export(name=func_name, funcidx=funcidx))

        def delete_export_function(self, idx=None, func_name=None):

            if idx is not None:
                export_rewriter = SectionRewriter(self.module, exportsec=self.module.export_sec)
                export_rewriter.delete(Export(exportidx=idx))
                return
            if func_name is not None:
                export_rewriter = SectionRewriter(self.module, exportsec=self.module.export_sec)
                export_function = export_rewriter.select(Export(name=func_name))
                export_rewriter.delete(export_function[0].exportidx)

        def append_export_function(self, func_name, funcidx):

            export_rewriter = SectionRewriter(self.module, exportsec=self.module.export_sec)
            export_rewriter.insert(None, inserted_item=Export(name=func_name, funcidx=funcidx))

        # def insert_import_global_variable(self, idx, module_name, variable_name, valtype):
        #     import_variable = Import(module_name, variable_name, ImportDesc(3, global_type=valtype))
        #     for _, import_item in enumerate(self.module.import_sec):
        #         if import_item == import_variable:
        #             raise Exception("The global variable already exists")
        #     self.section_rewriter.insert_importsec_import(idx, import_variable)
        #
        #     # fix
        #     pass
        #
        # def modify_import_global_variable(self, idx, module_name, variable_name, valtype):
        #     import_variable = Import(module_name, variable_name, ImportDesc(3, global_type=valtype))
        #     for _, import_item in enumerate(self.module.import_sec):
        #         if import_item == import_variable:
        #             raise Exception("The global variable already exists")
        #     self.module.import_sec[idx] = import_variable
        #
        #     # fix
        #     for code in self.section_rewriter.get_codesec_code_list():
        #         self.indices_fixer.fix_global_instructions(code.expr, idx)
        #
        # def insert_import_memory(self, idx, module_name, memory_name, limits):
        #     mem_list = self.section_rewriter.get_mem_list()
        #     memidx = None
        #     for _, mem in enumerate(mem_list):
        #         if mem == limits:
        #             memidx = _
        #     if memidx is None:
        #         memidx = self.section_rewriter.append_memsec_mem(limits)
        #
        #     import_mem = Import(module_name, memory_name, ImportDesc(2, mem=memidx))
        #     self.section_rewriter.insert_importsec_import(idx, import_mem)
        #
        #     # fix
        #     pass
        #
        # def modify_import_memory(self, idx, module_name, memory_name, limits):
        #     mem_list = self.section_rewriter.get_mem_list()
        #     memidx = None
        #     for _, mem in enumerate(mem_list):
        #         if mem == limits:
        #             memidx = _
        #     if memidx is None:
        #         memidx = self.section_rewriter.append_memsec_mem(limits)
        #
        #     import_mem = Import(module_name, memory_name, ImportDesc(2, mem=memidx))
        #     self.module.import_sec[idx] = import_mem
        #
        # def insert_import_table(self, idx, module_name, table_name, limits):
        #     table_list = self.section_rewriter.get_table_list()
        #     tableidx = None
        #     for _, table in enumerate(table_list):
        #         if table == limits:
        #             tableidx = _
        #     if tableidx is None:
        #         tableidx = self.section_rewriter.append_tablesec_table(limits)
        #
        #     import_table = Import(module_name, table_name, ImportDesc(1, table=tableidx))
        #     self.section_rewriter.insert_importsec_import(idx, import_table)
        #
        # def modify_import_table(self, idx, module_name, table_name, limits):
        #     table_list = self.section_rewriter.get_table_list()
        #     tableidx = None
        #     for _, table in enumerate(table_list):
        #         if table == limits:
        #             tableidx = _
        #     if tableidx is None:
        #         tableidx = self.section_rewriter.append_tablesec_table(limits)
        #
        #     import_table = Import(module_name, table_name, ImportDesc(1, table=tableidx))
        #     self.module.import_sec[idx] = import_table

    class LinearMemory:
        def __init__(self, module):
            self.module = module
            self.indices_fixer = IndicesFixer(self.module)

        def insert_linear_memory(self, offset, bytes):
            memory_rewriter = SectionRewriter(self.module, memsec=self.module.mem_sec)
            memory_list = memory_rewriter.select(Memory())

            if memory_list[0].max != 0 and offset + len(bytes) + 1 > memory_list[0].max * 65536:
                raise Exception("Memory out of bounds")

            data_rewriter = SectionRewriter(self.module, datasec=self.module.data_sec)

            is_overlap = False
            length = len(bytes)
            for data_item in data_rewriter.select(Data()):
                if offset + length < data_item.offset:
                    is_overlap = False
                elif data_item.offset + len(data_item.init_data) < offset:
                    is_overlap = False
                elif offset + length >= data_item.offset:
                    is_overlap = True
                    if offset >= data_item.offset:
                        data_item.init_data = data_item.init_data[:(offset - data_item.offset)] + bytearray(
                            bytes) + data_item.init_data[(offset - data_item.offset):]
                    else:
                        data_item.offset -= (offset - data_item.offset)
                        data_item.init_data = bytearray(bytes) + data_item.init_data

                self.indices_fixer.fix_memory_limits(self.module.mem_sec, offset + length)

            if data_rewriter.select(Data()) is [] or is_overlap is False:
                data_rewriter.insert(None, inserted_item=Data(offset=offset, init_data=bytes))

        def append_linear_memory(self, page_num):
            memory_rewriter = SectionRewriter(self.module, memsec=self.module.mem_sec)
            mem_list = memory_rewriter.select(Memory())

            if mem_list[0].max != 0:
                mem_list[0].max += page_num

        def modify_linear_memory(self, offset, bytes):
            memory_rewriter = SectionRewriter(self.module, memsec=self.module.mem_sec)
            mem_list = memory_rewriter.select(Memory())

            if mem_list[0].max != 0 and offset + len(bytes) + 1 > mem_list[0].max * 65536:
                raise Exception("Memory out of bounds")

            data_rewriter = SectionRewriter(self.module, datasec=self.module.data_sec)
            data_rewriter.insert(None, inserted_item=Data(offset=offset, init_data=bytes))

    class Function:
        def __init__(self, module):
            self.module = module

        def insert_internal_function(self, idx, params_type, results_type, local_vec, func_body):

            import_rewriter = SectionRewriter(self.module, importsec=self.module.import_sec)
            import_func_num = len(import_rewriter.select(Import()))

            if import_func_num > idx:
                raise Exception("The idx of internal function less than import function")

            type_rewriter = SectionRewriter(self.module, typesec=self.module.type_sec)
            result = type_rewriter.select(Type(arg_types=params_type, ret_types=results_type))
            if result == []:
                type_rewriter.insert(None, inserted_item=Type(arg_types=params_type, ret_types=results_type))
                typeidx = type_rewriter.select(Type())[-1].typeidx
            else:
                typeidx = result[0].typeidx

            function_rewriter = SectionRewriter(self.module, funcsec=self.module.func_sec)
            function_rewriter.insert(Function(funcidx=idx), Function(typeidx=typeidx))

            code_rewriter = SectionRewriter(self.module, codesec=self.module.code_sec)
            code_rewriter.insert(Code(funcidx=idx), Code(local_vec=local_vec, instr_list=func_body))

        def insert_indirect_function(self, idx, params_type, results_type, local_vec, func_body):

            self.insert_internal_function(idx, params_type, results_type, local_vec, func_body)

            element_rewriter = SectionRewriter(self.module, elemsec=self.module.elem_sec)

            # get original indirect function list
            indirect_func_list = []
            for elem in element_rewriter.select(Element()):
                indirect_func_list.extend(elem.funcidx_list)

            element_list = element_rewriter.select(Element())

            if not element_list:
                element_rewriter.insert(None, inserted_item=Element(tableidx=0, offset=1, funcidx_list=[idx]))
            else:
                element_list[0].funcidx_list.append(idx)
                element_rewriter.update(Element(elemidx=element_list[0].elemidx), element_list[0])

        def insert_hook_function(self, hooked_funcidx, idx, params_type, results_type, locals_vec, func_body):
            self.insert_internal_function(idx, params_type, results_type, locals_vec, func_body)

            import_rewriter = SectionRewriter(self.module, importsec=self.module.import_sec)
            import_func_num = len(import_rewriter.select(Import()))

            code_rewriter = SectionRewriter(self.module, codesec=self.module.code_sec)

            for funcidx in range(import_func_num, import_func_num + len(code_rewriter.select(Code()))):
                if funcidx != idx:
                    code = code_rewriter.select(Code(funcidx=funcidx))
                    for instr in code.instr_list:
                        if instr == Instruction(Call, hooked_funcidx):
                            instr.opcode = Call
                            instr.args = idx
                    code_rewriter.update(Code(funcidx=funcidx), Code(instr_list=code.instr_list))

            return idx

        # def change_func_instr(self, binary, funcidx, offset, instr):
        #     import_func_num = self.section_rewriter.get_import_func_num()
        #     if funcidx < import_func_num:
        #         raise Exception("funcidx error")
        #     code = self.section_rewriter.get_codesec_code(binary, funcidx - import_func_num)
        #
        #     self.section_rewriter.modify_code_instr(code, offset, instr)

        def delete_func_instr(self, funcidx, offset):

            import_rewriter = SectionRewriter(self.module, importsec=self.module.import_sec)
            import_func_num = len(import_rewriter.select(Import()))

            if funcidx < import_func_num:
                raise Exception("funcidx error")

            code_rewriter = SectionRewriter(self.module, codesec=self.module.code_sec)
            code_list = code_rewriter.select(Code(funcidx=funcidx))

            code_list[0].instr_list.pop(offset)
            code_rewriter.update(Code(funcidx=funcidx), code_list[0])

        def insert_func_instrs(self, funcidx, offset, instrs: list):

            import_rewriter = SectionRewriter(self.module, importsec=self.module.import_sec)
            import_func_num = len(import_rewriter.select(Import()))

            if funcidx < import_func_num:
                raise Exception("funcidx error")

            code_rewriter = SectionRewriter(self.module, codesec=self.module.code_sec)
            code_list = code_rewriter.select(Code(funcidx=funcidx))

            for i in reversed(instrs):
                code_list[0].instr_list.insert(offset, i)

            code_rewriter.update(Code(funcidx=funcidx), code_list[0])

        def append_func_instrs(self, funcidx, instrs: list):

            import_rewriter = SectionRewriter(self.module, importsec=self.module.import_sec)
            import_func_num = len(import_rewriter.select(Import()))

            if funcidx < import_func_num:
                raise Exception("funcidx error")

            code_rewriter = SectionRewriter(self.module, codesec=self.module.code_sec)
            code_list = code_rewriter.select(Code(funcidx=funcidx))

            code_list[0].instr_list.extend(instrs)
            code_rewriter.update(Code(funcidx=funcidx), code_list[0])

        def modify_func_instrs(self, funcidx, instr, instrs: list):
            import_rewriter = SectionRewriter(self.module, importsec=self.module.import_sec)
            import_func_num = len(import_rewriter.select(Import()))

            if funcidx < import_func_num:
                raise Exception("funcidx error")

            code_rewriter = SectionRewriter(self.module, codesec=self.module.code_sec)
            code_list = code_rewriter.select(Code(funcidx=funcidx))

            for index, i in enumerate(code_list[0].instr_list):
                if i == instr:
                    code_list[0].instr_list.pop(index)
                    for j in reversed(instrs):
                        code_list[0].instr_list.insert(index, j)

            code_rewriter.update(Code(funcidx=funcidx), Code(instr_list=code_list[0].instr_list))

        def append_func_local(self, funcidx, valtype):
            import_rewriter = SectionRewriter(self.module, importsec=self.module.import_sec)
            import_func_num = len(import_rewriter.select(Import()))

            if funcidx < import_func_num:
                raise Exception("funcidx error")

            code_rewriter = SectionRewriter(self.module, codesec=self.module.code_sec)
            code = code_rewriter.select(Code(funcidx=funcidx))
            code.local_vec.append(Local(len(code.local_vec), valtype))

            code_rewriter.update(Code(funcidx=funcidx), Code(instr_list=code.instr_list))

    class CustomContent:
        def __init__(self, module):
            self.module = module

        def modify_func_name(self, funcidx, name):
            namesec = self.section_rewriter.get_customsec_custom(name="name")
            funcname_list = self.section_rewriter.get_namesec_funcname_list(namesec)
            for _, funcname in enumerate(funcname_list):
                if funcname.idx == funcidx:
                    funcname_list[_].name = name

        def delete_func_name(self, funcidx):
            namesec = self.section_rewriter.get_customsec_custom(name="name")
            funcname_list = self.section_rewriter.get_namesec_funcname_list(namesec)
            for _, funcname in enumerate(funcname_list):
                if funcname.idx == funcidx:
                    funcname_list.pop(_)

        def insert_func_name(self, funcidx, name):
            namesec = self.section_rewriter.get_customsec_custom(name="name")
            funcname_list = self.section_rewriter.get_namesec_funcname_list(namesec)
            for _, funcname in enumerate(funcname_list):
                if funcname.idx == (funcidx - 1):
                    funcname_list.insert(_ + 1, NameAssoc(funcidx, name))
                    return

        def insert_global_name(self, globalidx, name):
            namesec = self.section_rewriter.get_customsec_custom(name="name")
            globalname_list = self.section_rewriter.get_namesec_globalname_list(namesec)
            globalname_list.insert(globalidx, NameAssoc(globalidx, name))

        def delete_global_name(self, globalidx):
            namesec = self.section_rewriter.get_customsec_custom(name="name")
            globalname_list = self.section_rewriter.get_namesec_globalname_list(namesec)
            globalname_list.pop(globalidx)

        def modify_global_name(self, globalidx, name):
            namesec = self.section_rewriter.get_customsec_custom(name="name")
            globalname_list = self.section_rewriter.get_namesec_globalname_list(namesec)
            globalname_list[globalidx].name = name

        def insert_data_name(self, dataidx, name):
            namesec = self.section_rewriter.get_customsec_custom(name="name")
            dataname_list = self.section_rewriter.get_namesec_dataname_list(namesec)
            dataname_list.insert(dataidx, NameAssoc(dataidx, name))

        def delete_data_name(self, dataidx):
            namesec = self.section_rewriter.get_customsec_custom(name="name")
            dataname_list = self.section_rewriter.get_namesec_dataname_list(namesec)
            dataname_list.pop(dataidx)

        def modify_data_name(self, dataidx, name):
            namesec = self.section_rewriter.get_customsec_custom(name="name")
            dataname_list = self.section_rewriter.get_namesec_dataname_list(namesec)
            dataname_list[dataidx].name = name
