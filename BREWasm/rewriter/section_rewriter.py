from BREWasm.parser import module
from BREWasm.rewriter.modify_binary import ModifyBinary
from BREWasm.rewriter.defination import *
from BREWasm.rewriter.indices_fixer import *
from BREWasm.parser.instruction import Instruction
from BREWasm.rewriter.indices_fixer import IndicesFixer
#     def __init__(self, index, instr, instrs):
#         self.instr = instr
class SectionRewriter:

    def __init__(self, module, **section):
        allowed_params = ['typesec', 'importsec', 'funcsec', 'tablesec', 'memsec',
                          'globalsec', 'exportsec', 'startsec', 'elemsec', 'codesec',
                          'datasec', 'datacountsec', 'customsec']

        if len(section) != 1:
            raise ValueError("Only one parameter should be provided")

        param_name = next(iter(section.keys()))
        if param_name not in allowed_params:
            raise ValueError("Invalid parameter")

        self.module = module
        self.typesec = None
        self.importsec = None
        self.funcsec = None
        self.tablesec = None
        self.memsec = None
        self.globalsec = None
        self.exportsec = None
        self.startsec = None
        self.elemsec = None
        self.codesec = None
        self.datasec = None
        self.datacountsec = None
        self.customsec = None
        self.indices_fixer = IndicesFixer(module)

        setattr(self, param_name, section[param_name])

    def select(self, query):
        if self.typesec is not None and isinstance(query, Type):
            type_list = []
            for idx, item in enumerate(self.module.type_sec):
                param_types, result_types = item.get_signature()
                if all(
                        (query.typeidx is None or query.typeidx == idx,
                         query.arg_types is None or query.arg_types == param_types,
                         query.ret_types is None or query.ret_types == result_types,)
                ):
                    type_list.append(Type(idx, param_types, result_types))
            return type_list

        elif self.importsec is not None and isinstance(query, Import):

            import_list = []
            for idx, item in enumerate(self.module.import_sec):
                if item.desc.func_type is not None:
                    if all(
                            (query.importidx is None or query.importidx == idx,
                             query.module is None or query.module == item.module,
                             query.name is None or query.name == item.name,
                             query.typeidx is None or query.typeidx == item.desc.func_type)
                    ):
                        import_list.append(Import(idx, item.module, item.name, item.desc.func_type))
            return import_list

        elif self.funcsec is not None and isinstance(query, Function):
            function_list = []
            import_func_num = 0
            for import_func in self.module.import_sec:
                if import_func.desc.func_type is not None:
                    import_func_num += 1

            if query.funcidx is not None:
                query.funcidx -= import_func_num

            for idx, item in enumerate(self.module.func_sec):
                if all(
                        (query.funcidx is None or query.funcidx == idx,
                         query.typeidx is None or query.typeidx == item)
                ):
                    function_list.append(Function(idx + import_func_num, item))
            return function_list

        elif self.tablesec is not None and isinstance(query, Table):
            table_list = []
            for idx, item in enumerate(self.module.table_sec):
                if all(
                        (query.min is None or query.min == item.limits.min,
                         query.max is None or query.max == item.limits.max)
                ):
                    table_list.append(Table(item.limits.min, item.limits.max))
            return table_list

        elif self.memsec is not None and isinstance(query, Memory):
            mem_list = []
            for idx, item in enumerate(self.module.mem_sec):
                if all(
                        (query.min is None or query.min == item.min,
                         query.max is None or query.max == item.max)
                ):
                    mem_list.append(Memory(item.min, item.max))
            return mem_list

        elif self.globalsec is not None and isinstance(query, Global):
            global_list = []
            for idx, item in enumerate(self.module.global_sec):
                if all(
                        (query.globalidx is None or query.globalidx == idx,
                         query.valtype is None or query.valtype == item.type.val_type,
                         query.mut is None or query.mut == item.type.mut,
                         query.val is None or query.val == item.init[0].args)
                ):
                    global_list.append(Global(idx, item.type.val_type, item.type.mut, item.init[0].args))
            return global_list

        elif self.exportsec is not None and isinstance(query, Export):
            export_list = []
            for idx, item in enumerate(self.module.export_sec):
                if all(
                        (query.exportidx is None or query.exportidx == idx,
                         query.name is None or query.name == item.name,
                         query.funcidx is None or query.funcidx == item.desc.idx)
                ) and item.desc.tag == 0:
                    export_list.append(Export(idx, name=item.name, funcidx=item.desc.idx))
            return export_list

        elif self.startsec is not None and isinstance(query, Start):
            match query:
                case Start(funcidx=funcidx):
                    return Start(self.module.start_sec)
                case Start():
                    return Start(self.module.start_sec)

        elif self.elemsec is not None and isinstance(query, Element):
            element_list = []
            for idx, item in enumerate(self.module.elem_sec):
                if all(
                        (query.elemidx is None or query.elemidx == idx,
                         query.tableidx is None or query.tableidx == item.table,
                         query.offset is None or query.offset == item.offset[0].args)
                ):
                    element_list.append(
                        Element(idx, tableidx=item.table, offset=item.offset[0].args, funcidx_list=item.init))
            return element_list

        elif self.codesec is not None and isinstance(query, Code):
            code_list = []
            import_func_num = 0
            for import_func in self.module.import_sec:
                if import_func.desc.func_type is not None:
                    import_func_num += 1
            if query.funcidx < import_func_num:
                raise Exception("Import function!")
            query.funcidx -= import_func_num
            for idx, item in enumerate(self.module.code_sec):
                if query.funcidx is None or query.funcidx == idx:
                    locals = []
                    i = 0
                    for local in item.locals:
                        for j in range(i, i + local.n):
                            locals.append(Local(j, local.type))
                        i += local.n
                    instrs = self.get_flat_instrs(item.expr)
                    code_list.append(Code(idx + import_func_num, locals, instrs))
            return code_list

        elif self.datasec is not None and isinstance(query, Data):
            data_list = []
            for idx, item in enumerate(self.module.data_sec):
                if all(
                        (query.dataidx is None or query.dataidx == idx,
                         query.offset is None or query.offset == item.offset[0].args)
                ):
                    data_list.append(Data(idx, item.offset[0].args, item.init))
            return data_list

        elif self.datacountsec is not None:
            pass
        elif self.customsec is not None and isinstance(query, CustomName):
            name_list = []
            match query.name_type:
                case 0:
                    for custom in self.module.custom_secs:
                        if custom.name == "name":
                            for idx, item in enumerate(custom.name_data.funcNameSubSec):
                                if all(
                                        (query.idx is None or query.idx == item.idx,
                                         query.name is None or query.name == item.name)
                                ):
                                    name_list.append(CustomName(FunctionName, item.idx, item.name))
                case 1:
                    for custom in self.module.custom_secs:
                        if custom.name == "name":
                            for idx, item in enumerate(custom.name_data.globalNameSubSec):
                                if all(
                                        (query.idx is None or query.idx == item.idx,
                                         query.name is None or query.name == item.name)
                                ):
                                    name_list.append(CustomName(GlobalName, item.idx, item.name))
                case 2:
                    for custom in self.module.custom_secs:
                        if custom.name == "name":
                            for idx, item in enumerate(custom.name_data.dataNameSubSec):
                                if all(
                                        (query.idx is None or query.idx == item.idx,
                                         query.name is None or query.name == item.name)
                                ):
                                    name_list.append(CustomName(DataName, item.idx, item.name))
                case _:
                    pass
            return name_list
        else:
            raise Exception("error")

    def insert(self, query, inserted_item):

        if self.typesec is not None and isinstance(inserted_item, Type):
            if query is None:
                self.module.type_sec.append(inserted_item.convert())
            elif isinstance(query, Type):
                type_list = []
                for idx, item in enumerate(self.module.type_sec):
                    param_types, result_types = item.get_signature()
                    if all(
                            (query.typeidx is None or query.typeidx == idx,
                             query.arg_types is None or query.arg_types == param_types,
                             query.ret_types is None or query.ret_types == result_types,)
                    ):
                        type_list.append(Type(idx, param_types, result_types))
                if len(type_list) != 1:
                    raise Exception("error")

                idx = type_list[0].typeidx
                self.module.type_sec.insert(idx, inserted_item.convert())
                self.indices_fixer.fix_func_functypeidx(self.module.func_sec, idx)
                self.indices_fixer.fix_import_func_functypeidx(self.module.import_sec, idx)

        elif self.importsec is not None and isinstance(inserted_item, Import):
            if query is None:
                self.module.import_sec.append(module.Import(inserted_item.module, inserted_item.name,
                                                            module.ImportDesc(tag=0,
                                                                              func_type=inserted_item.typeidx)))
            elif isinstance(query, Import):
                import_list = []
                for idx, item in enumerate(self.module.import_sec):
                    if item.desc.func_type is not None:
                        if all(
                                (query.importidx is None or query.importidx == idx,
                                 query.module is None or query.module == item.module,
                                 query.name is None or query.name == item.name,
                                 query.typeidx is None or query.typeidx == item.desc.func_type)
                        ):
                            import_list.append(Import(idx, item.module, item.name, item.desc.func_type))

                if len(import_list) != 1:
                    raise Exception("error")

                idx = import_list[0].importidx

                self.module.import_sec.insert(idx, module.Import(inserted_item.module, inserted_item.name,
                                                                 module.ImportDesc(tag=0,
                                                                                   func_type=inserted_item.typeidx)))
            import_func_id = None
            for i, import_item in enumerate([i for i in self.module.import_sec if i.desc.func_type is not None]):
                if import_item.module == inserted_item.module and import_item.name == inserted_item.name:
                    import_func_id = i
            for _, code in enumerate(self.module.code_sec):
                self.indices_fixer.fix_call_instructions(code.expr, import_func_id)
            self.indices_fixer.fix_elem_funcidx(self.module.elem_sec, import_func_id)
            self.indices_fixer.fix_export_funcidx(self.module.export_sec, import_func_id)

        elif self.funcsec is not None and isinstance(inserted_item, Function):
            if query is None:
                self.module.func_sec.append(inserted_item.typeidx)
            elif isinstance(query, Function):
                function_list = []
                import_func_num = 0
                for import_func in self.module.import_sec:
                    if import_func.desc.func_type is not None:
                        import_func_num += 1

                if query.funcidx is not None:
                    query.funcidx -= import_func_num

                for idx, item in enumerate(self.module.func_sec):
                    if all(
                            (query.funcidx is None or query.funcidx == idx,
                             query.typeidx is None or query.typeidx == item)
                    ):
                        function_list.append(Function(idx + import_func_num, item))

                if len(function_list) != 1:
                    raise Exception("error")

                idx = function_list[0].funcidx
                self.module.func_sec.insert(idx - import_func_num, inserted_item.typeidx)
                self.indices_fixer.fix_export_funcidx(self.module.export_sec, idx)
                self.indices_fixer.fix_elem_funcidx(self.module.elem_sec, idx)
                for _, code in enumerate(self.module.code_sec):
                    self.indices_fixer.fix_call_instructions(code.expr, idx)
        # elif self.tablesec is not None and isinstance(query, Table):
        #     table_list = []
        #         if all(
        #                  query.max is None or query.max == item.limits.max)
        #             table_list.append(Table(item.limits.min, item.limits.max))
        #     if len(table_list) != 1:
        #
        #
        #
        #
        #     mem_list = []
        #         if all(
        #                  query.max is None or query.max == item.max)
        #             mem_list.append(Memory(item.min, item.max))
        elif self.globalsec is not None and isinstance(inserted_item, Global):
            if inserted_item.valtype == ValTypeI32:
                init_value_instr = Instruction(I32Const, inserted_item.val)
            elif inserted_item.valtype == ValTypeI64:
                init_value_instr = Instruction(I64Const, inserted_item.val)
            elif inserted_item.valtype == ValTypeF32:
                init_value_instr = Instruction(F32Const, inserted_item.val)
            elif inserted_item.valtype == ValTypeF64:
                init_value_instr = Instruction(F64Const, inserted_item.val)
            else:
                raise Exception("global type error!")
            if inserted_item.mut is None:
                inserted_item.mut = 0

            if query is None:
                self.module.global_sec.append(module.Global(GlobalType(inserted_item.valtype, inserted_item.mut),
                                                            [init_value_instr]))
            elif isinstance(query, Global):
                global_list = []
                for idx, item in enumerate(self.module.global_sec):
                    if all(
                            (query.globalidx is None or query.globalidx == idx,
                             query.valtype is None or query.valtype == item.type.val_type,
                             query.mut is None or query.mut == item.type.mut,
                             query.val is None or query.val == item.init[0].args)
                    ):
                        global_list.append(Global(idx, item.type.val_type, item.type.mut, item.init[0].args))

                if len(global_list) != 1:
                    raise Exception("error")
                idx = global_list[0].globalidx
                self.module.global_sec.insert(idx, module.Global(GlobalType(inserted_item.valtype, inserted_item.mut),
                                                                 [init_value_instr]))
                self.indices_fixer.fix_export_globalidx(self.module.export_sec, idx)
                for code in self.module.code_sec:
                    self.indices_fixer.fix_global_instructions(code.expr, idx)

        elif self.exportsec is not None and isinstance(inserted_item, Export):
            if query is None:
                self.module.export_sec.append(
                    module.Export(inserted_item.name, module.ExportDesc(0, inserted_item.funcidx)))
            elif isinstance(query, Export):
                export_list = []
                for idx, item in enumerate(self.module.export_sec):
                    if all(
                            (query.exportidx is None or query.exportidx == idx,
                             query.name is None or query.name == item.name,
                             query.funcidx is None or query.funcidx == item.desc.idx)
                    ):
                        export_list.append(Export(idx, name=item.name, funcidx=item.desc.idx))

                if len(export_list) != 1:
                    raise Exception("error")

                idx = export_list[0].exportidx
                self.module.export_sec.insert(idx, module.Export(inserted_item.name,
                                                                 module.ExportDesc(0, inserted_item.funcidx)))

        elif self.startsec is not None and isinstance(inserted_item, Start):
            match query:
                case Start(funcidx=funcidx):
                    return Start(self.module.start_sec)
                case Start():
                    return Start(self.module.start_sec)

        elif self.elemsec is not None and isinstance(inserted_item, Element):
            element_list = []
            for idx, item in enumerate(self.module.elem_sec):
                if all(
                        (query.elemidx is None or query.elemidx == idx,
                         query.tableidx is None or query.tableidx == item.table,
                         query.offset is None or query.offset == item.offset[0].args)
                ):
                    element_list.append(
                        Element(idx, tableidx=item.table, offset=item.offset[0].args, funcidx_list=item.init))
            return element_list

        elif self.codesec is not None and isinstance(inserted_item, Code):
            locals = inserted_item.convert_local_vec()
            fold_instrs = self.get_fold_instrs(inserted_item.instr_list)

            if query is None:
                self.module.code_sec.append(module.Code(locals, fold_instrs))
            elif isinstance(query, Code):

                code_list = []
                import_func_num = 0
                for import_func in self.module.import_sec:
                    if import_func.desc.func_type is not None:
                        import_func_num += 1
                if query.funcidx < import_func_num:
                    raise Exception("Import function!")
                query.funcidx -= import_func_num
                for idx, item in enumerate(self.module.code_sec):
                    if query.funcidx is None or query.funcidx == idx:
                        local_vec = []
                        i = 0
                        for local in item.locals:
                            for j in range(i, i + local.n):
                                local_vec.append(Local(j, local.type))
                            i += local.n
                        instrs = self.get_flat_instrs(item.expr)
                        code_list.append(Code(idx + import_func_num, local_vec, instrs))

                if len(code_list) != 1:
                    raise Exception("error")

                idx = code_list[0].funcidx - import_func_num

                self.module.code_sec.insert(idx, module.Code(locals, fold_instrs))

        elif self.datasec is not None and isinstance(inserted_item, Data):
            data_list = []
            if query is None:
                self.module.data_sec.append(module.Data(inserted_item.dataidx, Instruction(I32Const, inserted_item.offset), inserted_item.init_data))
            else:
                for idx, item in enumerate(self.module.data_sec):
                    if all(
                            (query.dataidx is None or query.dataidx == idx,
                             query.offset is None or query.offset == item.offset[0].args)
                    ):
                        data_list.append(Data(idx, item.offset[0].args, item.init))
                return data_list

        elif self.datacountsec is not None:
            pass
        elif self.customsec is not None and isinstance(inserted_item, CustomName):
            name_list = []
            match query.name_type:
                case 0:
                    for custom in self.module.custom_secs:
                        if custom.name == "name":
                            for idx, item in enumerate(custom.name_data.funcNameSubSec):
                                if all(
                                        (query.idx is None or query.idx == item.idx,
                                         query.name is None or query.name == item.name)
                                ):
                                    name_list.append(CustomName(FunctionName, item.idx, item.name))
                case 1:
                    for custom in self.module.custom_secs:
                        if custom.name == "name":
                            for idx, item in enumerate(custom.name_data.globalNameSubSec):
                                if all(
                                        (query.idx is None or query.idx == item.idx,
                                         query.name is None or query.name == item.name)
                                ):
                                    name_list.append(CustomName(GlobalName, item.idx, item.name))
                case 2:
                    for custom in self.module.custom_secs:
                        if custom.name == "name":
                            for idx, item in enumerate(custom.name_data.dataNameSubSec):
                                if all(
                                        (query.idx is None or query.idx == item.idx,
                                         query.name is None or query.name == item.name)
                                ):
                                    name_list.append(CustomName(DataName, item.idx, item.name))
                case _:
                    pass
            return name_list
        else:
            raise Exception("error")

    def delete(self, query):

        if self.typesec is not None and isinstance(query, Type):
            type_list = []
            for idx, item in enumerate(self.module.type_sec):
                param_types, result_types = item.get_signature()
                if all(
                        (query.typeidx is None or query.typeidx == idx,
                         query.arg_types is None or query.arg_types == param_types,
                         query.ret_types is None or query.ret_types == result_types,)
                ):
                    type_list.append(Type(idx, param_types, result_types))
            if len(type_list) != 1:
                raise Exception("error")

            idx = type_list[0].typeidx
            self.module.type_sec.pop(idx)
            self.indices_fixer.fix_func_functypeidx(self.module.func_sec, idx, type=Delete)
            self.indices_fixer.fix_import_func_functypeidx(self.module.import_sec, idx, type=Delete)

        elif self.importsec is not None and isinstance(query, Import):

            import_list = []
            for idx, item in enumerate(self.module.import_sec):
                if item.desc.func_type is not None:
                    if all(
                            (query.importidx is None or query.importidx == idx,
                             query.module is None or query.module == item.module,
                             query.name is None or query.name == item.name,
                             query.typeidx is None or query.typeidx == item.desc.func_type)
                    ):
                        import_list.append(Import(idx, item.module, item.name, item.desc.func_type))

            if len(import_list) != 1:
                raise Exception("error")

            idx = import_list[0].importidx

            self.module.import_sec.pop(idx)
            import_func_id = None
            for i, import_item in enumerate([i for i in self.module.import_sec if i.desc.func_type is not None]):
                if import_item.module == item.module and import_item.name == item.name:
                    import_func_id = i
            for _, code in enumerate(self.module.code_sec):
                self.indices_fixer.fix_call_instructions(code.expr, import_func_id, type=Delete)
            self.indices_fixer.fix_elem_funcidx(self.module.elem_sec, import_func_id, type=Delete)
            self.indices_fixer.fix_export_funcidx(self.module.export_sec, import_func_id, type=Delete)

        elif self.funcsec is not None and isinstance(query, Function):
            function_list = []
            import_func_num = 0
            for import_func in self.module.import_sec:
                if import_func.desc.func_type is not None:
                    import_func_num += 1

            if query.funcidx is not None:
                query.funcidx -= import_func_num

            for idx, item in enumerate(self.module.func_sec):
                if all(
                        (query.funcidx is None or query.funcidx == idx,
                         query.typeidx is None or query.typeidx == item)
                ):
                    function_list.append(Function(idx + import_func_num, item))

            if len(function_list) != 1:
                raise Exception("error")

            idx = function_list[0].funcidx
            self.module.func_sec.pop(idx - import_func_num)
            self.indices_fixer.fix_export_funcidx(self.module.export_sec, idx, type=Delete)
            self.indices_fixer.fix_elem_funcidx(self.module.elem_sec, idx, type=Delete)
            for _, code in enumerate(self.module.code_sec):
                self.indices_fixer.fix_call_instructions(code.expr, idx, type=Delete)
        # elif self.tablesec is not None and isinstance(query, Table):
        #     table_list = []
        #         if all(
        #                  query.max is None or query.max == item.limits.max)
        #             table_list.append(Table(item.limits.min, item.limits.max))
        #     if len(table_list) != 1:
        #
        #
        #
        #
        #     mem_list = []
        #         if all(
        #                  query.max is None or query.max == item.max)
        #             mem_list.append(Memory(item.min, item.max))
        elif self.globalsec is not None and isinstance(query, Global):
            global_list = []
            for idx, item in enumerate(self.module.global_sec):
                if all(
                        (query.globalidx is None or query.globalidx == idx,
                         query.valtype is None or query.valtype == item.type.val_type,
                         query.mut is None or query.mut == item.type.mut,
                         query.val is None or query.val == item.init[0].args)
                ):
                    global_list.append(Global(idx, item.type.val_type, item.type.mut, item.init[0].args))

            if len(global_list) != 1:
                raise Exception("error")
            idx = global_list[0].globalidx

            self.module.global_sec.pop(idx)
            self.indices_fixer.fix_export_globalidx(self.module.export_sec, idx, type=Delete)
            for code in self.module.code_sec:
                self.indices_fixer.fix_global_instructions(code.expr, idx, type=Delete)

        elif self.exportsec is not None and isinstance(query, Export):
            export_list = []
            for idx, item in enumerate(self.module.export_sec):
                if all(
                        (query.exportidx is None or query.exportidx == idx,
                         query.name is None or query.name == item.name,
                         query.funcidx is None or query.funcidx == item.desc.idx)
                ) and item.desc.tag == 0:
                    export_list.append(Export(idx, name=item.name, funcidx=item.desc.idx))

            if len(export_list) != 1:
                raise Exception("error")

            idx = export_list[0].exportidx
            self.module.export_sec.pop(idx)

        elif self.startsec is not None and isinstance(query, Start):
            match query:
                case Start(funcidx=funcidx):
                    return Start(self.module.start_sec)
                case Start():
                    return Start(self.module.start_sec)

        elif self.elemsec is not None and isinstance(query, Element):
            element_list = []
            for idx, item in enumerate(self.module.elem_sec):
                if all(
                        (query.elemidx is None or query.elemidx == idx,
                         query.tableidx is None or query.tableidx == item.table,
                         query.offset is None or query.offset == item.offset[0].args)
                ):
                    element_list.append(
                        Element(idx, tableidx=item.table, offset=item.offset[0].args, funcidx_list=item.init))
            return element_list

        elif self.codesec is not None and isinstance(query, Code):
            code_list = []
            import_func_num = 0
            for import_func in self.module.import_sec:
                if import_func.desc.func_type is not None:
                    import_func_num += 1
            if query.funcidx < import_func_num:
                raise Exception("Import function!")
            query.funcidx -= import_func_num
            for idx, item in enumerate(self.module.code_sec):
                if query.funcidx is None or query.funcidx == idx:
                    locals = []
                    i = 0
                    for local in item.locals:
                        for j in range(i, i + local.n):
                            locals.append(Local(j, local.type))
                        i += local.n
                    instrs = self.get_flat_instrs(item.expr)
                    code_list.append(Code(idx + import_func_num, locals, instrs))

            if len(code_list) != 1:
                raise Exception("error")

            idx = code_list[0].funcidx

            self.module.code_sec.pop(idx)

        elif self.datasec is not None and isinstance(query, Data):
            data_list = []
            for idx, item in enumerate(self.module.data_sec):
                if all(
                        (query.dataidx is None or query.dataidx == idx,
                         query.offset is None or query.offset == item.offset[0].args)
                ):
                    self.module.data_sec.pop(idx)
            return data_list

        elif self.datacountsec is not None:
            pass
        elif self.customsec is not None and isinstance(query, CustomName):
            name_list = []
            match query.name_type:
                case 0:
                    for custom in self.module.custom_secs:
                        if custom.name == "name":
                            for idx, item in enumerate(custom.name_data.funcNameSubSec):
                                if all(
                                        (query.idx is None or query.idx == item.idx,
                                         query.name is None or query.name == item.name)
                                ):
                                    custom.name_data.funcNameSubSec.pop(idx)
                case 1:
                    for custom in self.module.custom_secs:
                        if custom.name == "name":
                            for idx, item in enumerate(custom.name_data.globalNameSubSec):
                                if all(
                                        (query.idx is None or query.idx == item.idx,
                                         query.name is None or query.name == item.name)
                                ):
                                    custom.name_data.globalNameSubSec.pop(idx)
                case 2:
                    for custom in self.module.custom_secs:
                        if custom.name == "name":
                            for idx, item in enumerate(custom.name_data.dataNameSubSec):
                                if all(
                                        (query.idx is None or query.idx == item.idx,
                                         query.name is None or query.name == item.name)
                                ):
                                    custom.name_data.dataNameSubSec.pop(idx)
                case _:
                    pass
            return name_list
        else:
            raise Exception("error")

    def update(self, query, new_item):

        if self.typesec is not None and isinstance(query, Type):
            type_list = []
            for idx, item in enumerate(self.module.type_sec):
                param_types, result_types = item.get_signature()
                if all(
                        (query.typeidx is None or query.typeidx == idx,
                         query.arg_types is None or query.arg_types == param_types,
                         query.ret_types is None or query.ret_types == result_types,)
                ):
                    type_list.append(Type(idx, param_types, result_types))
            for t in type_list:
                if new_item.arg_types is not None:
                    param_types = []
                    for arg in new_item.arg_types:
                        match arg:
                            case "i32":
                                param_types.append(ValTypeI32)
                            case "i64":
                                param_types.append(ValTypeI64)
                            case "f32":
                                param_types.append(ValTypeF32)
                            case "f64":
                                param_types.append(ValTypeF64)
                    self.module.type_sec[t.typeidx].param_types = param_types

                if new_item.ret_types is not None:
                    result_types = []
                    for arg in new_item.ret_types:
                        match arg:
                            case "i32":
                                result_types.append(ValTypeI32)
                            case "i64":
                                result_types.append(ValTypeI64)
                            case "f32":
                                result_types.append(ValTypeF32)
                            case "f64":
                                result_types.append(ValTypeF64)
                    t.result_types = result_types
                    self.module.type_sec[t.typeidx].result_types = result_types

        elif self.importsec is not None and isinstance(query, Import):

            import_list = []
            for idx, item in enumerate(self.module.import_sec):
                if item.desc.func_type is not None:
                    if all(
                            (query.importidx is None or query.importidx == idx,
                             query.module is None or query.module == item.module,
                             query.name is None or query.name == item.name,
                             query.typeidx is None or query.typeidx == item.desc.func_type)
                    ):
                        import_list.append(Import(idx, item.module, item.name, item.desc.func_type))
            for i in import_list:
                if new_item.module is not None:
                    self.module.import_sec[i.importidx].module = new_item.module
                if new_item.name is not None:
                    self.module.import_sec[i.importidx].name = new_item.name
                if new_item.typeidx is not None:
                    self.module.import_sec[i.importidx].desc.func_type = new_item.typeidx

        elif self.funcsec is not None and isinstance(query, Function):
            function_list = []
            import_func_num = 0
            for import_func in self.module.import_sec:
                if import_func.desc.func_type is not None:
                    import_func_num += 1

            if query.funcidx is not None:
                query.funcidx -= import_func_num

            for idx, item in enumerate(self.module.func_sec):
                if all(
                        (query.funcidx is None or query.funcidx == idx,
                         query.typeidx is None or query.typeidx == item)
                ):
                    function_list.append(Function(idx + import_func_num, item))
            for f in function_list:
                if new_item.typeidx is not None:
                    self.module.func_sec[f.funcidx - import_func_num] = new_item.typeidx

        elif self.tablesec is not None and isinstance(query, Table):
            table_list = []
            for idx, item in enumerate(self.module.table_sec):
                if all(
                        (query.min is None or query.min == item.limits.min,
                         query.max is None or query.max == item.limits.max)
                ):
                    table_list.append({
                        "idx": idx,
                        "table": Table(item.limits.min, item.limits.max)
                    })
            for t in table_list:
                if new_item.min is not None:
                    self.module.table_sec[t["idx"]].limits.min = new_item.min
                if new_item.max is not None:
                    self.module.table_sec[t["idx"]].limits.max = new_item.max

        elif self.memsec is not None and isinstance(query, Memory):
            mem_list = []
            for idx, item in enumerate(self.module.mem_sec):
                if all(
                        (query.min is None or query.min == item.min,
                         query.max is None or query.max == item.max)
                ):
                    mem_list.append({
                        "idx": idx,
                        "memory": Memory(item.min, item.max)
                    })
            for m in mem_list:
                if new_item.min is not None:
                    self.module.mem_sec[m["idx"]].min = new_item.min
                if new_item.max is not None:
                    self.module.mem_sec[m["idx"]].max = new_item.max

        elif self.globalsec is not None and isinstance(query, Global):
            global_list = []
            for idx, item in enumerate(self.module.global_sec):
                if all(
                        (query.globalidx is None or query.globalidx == idx,
                         query.valtype is None or query.valtype == item.type.val_type,
                         query.mut is None or query.mut == item.type.mut,
                         query.val is None or query.val == item.init[0].args)
                ):
                    global_list.append(Global(idx, item.type.val_type, item.type.mut, item.init[0].args))

            for g in global_list:
                if new_item.valtype is not None:
                    self.module.global_sec[g.globalidx].type.val_type = new_item.valtype
                if new_item.mut is not None:
                    self.module.global_sec[g.globalidx].type.mut = new_item.mut
                if new_item.val is not None:
                    if self.module.global_sec[g.globalidx].type.val_type == ValTypeI32:
                        init_value_instr = Instruction(I32Const, new_item.val)
                    elif self.module.global_sec[g.globalidx].type.val_type == ValTypeI64:
                        init_value_instr = Instruction(I64Const, new_item.val)
                    elif self.module.global_sec[g.globalidx].type.val_type == ValTypeF32:
                        init_value_instr = Instruction(F32Const, new_item.val)
                    elif self.module.global_sec[g.globalidx].type.val_type == ValTypeF64:
                        init_value_instr = Instruction(F64Const, new_item.val)
                    self.module.global_sec[g.globalidx].init[0] = init_value_instr

        elif self.exportsec is not None and isinstance(query, Export):
            export_list = []
            for idx, item in enumerate(self.module.export_sec):
                if all(
                        (query.exportidx is None or query.exportidx == idx,
                         query.name is None or query.name == item.name,
                         query.funcidx is None or query.funcidx == item.desc.idx)
                ) and item.desc.tag == 0:
                    export_list.append(Export(idx, name=item.name, funcidx=item.desc.idx))
            for e in export_list:
                if new_item.name is not None:
                    self.module.export_sec[e.exportidx].name = new_item.name
                if new_item.funcidx is not None:
                    self.module.export_sec[e.exportidx].desc.idx = new_item.funcidx
        #     match query:
        #             return Start(self.module.start_sec)
        #             return Start(self.module.start_sec)

        elif self.elemsec is not None and isinstance(query, Element):
            element_list = []
            for idx, item in enumerate(self.module.elem_sec):
                if all(
                        (query.elemidx is None or query.elemidx == idx,
                         query.tableidx is None or query.tableidx == item.table,
                         query.offset is None or query.offset == item.offset[0].args)
                ):
                    element_list.append(
                        Element(idx, tableidx=item.table, offset=item.offset[0].args, funcidx_list=item.init))
            for e in element_list:
                if new_item.tableidx is not None:
                    self.module.elem_sec[e.elemidx].table = new_item.tableidx
                if new_item.offset is not None:
                    self.module.elem_sec[e.elemidx].offset = [Instruction(I32Const, new_item.offset)]
                if new_item.funcidx_list is not None:
                    self.module.elem_sec[e.elemidx].init = new_item.funcidx_list

                indirect_func_list = e.funcidx_list
                self.indices_fixer.fix_table_limits(self.module.table_sec, len(indirect_func_list) + 1)

        elif self.codesec is not None and isinstance(query, Code):
            code_list = []
            import_func_num = 0
            for import_func in self.module.import_sec:
                if import_func.desc.func_type is not None:
                    import_func_num += 1
            if query.funcidx < import_func_num:
                raise Exception("Import function!")
            query.funcidx -= import_func_num
            for idx, item in enumerate(self.module.code_sec):
                if query.funcidx is None or query.funcidx == idx:
                    locals = []
                    i = 0
                    for local in item.locals:
                        for j in range(i, i + local.n):
                            locals.append(Local(j, local.type))
                        i += local.n
                    instrs = self.get_flat_instrs(item.expr)
                    code_list.append(Code(idx + import_func_num, locals, instrs))
            for c in code_list:
                if new_item.local_vec is not None:
                    self.module.code_sec[c.funcidx - import_func_num].locals = new_item.convert_local_vec()
                if new_item.instr_list is not None:
                    self.module.code_sec[c.funcidx - import_func_num].expr = self.get_fold_instrs(new_item.instr_list)



        elif self.datasec is not None and isinstance(query, Data):
            data_list = []
            for idx, item in enumerate(self.module.data_sec):
                if all(
                        (query.dataidx is None or query.dataidx == idx,
                         query.offset is None or query.offset == item.offset[0].args)
                ):
                    data_list.append(Data(idx, item.offset[0].args, item.init))
            for d in data_list:
                if new_item.offset is not None:
                    self.module.data_sec[d.dataidx].offset = [Instruction(I32Const, new_item.offset)]
                if new_item.init_data is not None:
                    self.module.data_sec[d.dataidx].init = new_item.init_data

        elif self.datacountsec is not None:
            pass
        elif self.customsec is not None and isinstance(query, CustomName):
            name_list = []
            match query.name_type:
                case 0:
                    for custom in self.module.custom_secs:
                        if custom.name == "name":
                            for idx, item in enumerate(custom.name_data.funcNameSubSec):
                                if all(
                                        (query.idx is None or query.idx == item.idx,
                                         query.name is None or query.name == item.name)
                                ):
                                    name_list.append(CustomName(FunctionName, item.idx, item.name))
                case 1:
                    for custom in self.module.custom_secs:
                        if custom.name == "name":
                            for idx, item in enumerate(custom.name_data.globalNameSubSec):
                                if all(
                                        (query.idx is None or query.idx == item.idx,
                                         query.name is None or query.name == item.name)
                                ):
                                    name_list.append(CustomName(GlobalName, item.idx, item.name))
                case 2:
                    for custom in self.module.custom_secs:
                        if custom.name == "name":
                            for idx, item in enumerate(custom.name_data.dataNameSubSec):
                                if all(
                                        (query.idx is None or query.idx == item.idx,
                                         query.name is None or query.name == item.name)
                                ):
                                    name_list.append(CustomName(DataName, item.idx, item.name))
                case _:
                    pass
            name_section_idx = None
            for i, custom_sec in enumerate(self.module.custom_secs):
                if custom_sec.name == "name":
                    name_section_idx = i

            for n in name_list:
                if new_item.name is not None:
                    match n.name_type:
                        case 0:
                            self.module.custom_secs[name_section_idx].name_data.funcNameSubSec[
                                n.idx].name = new_item.name
                        case 1:
                            self.module.custom_secs[name_section_idx].name_data.globalNameSubSec[
                                n.idx].name = new_item.name
                        case 2:
                            self.module.custom_secs[name_section_idx].name_data.dataNameSubSec[
                                n.idx].name = new_item.name
                        case _:
                            pass

        else:
            raise Exception("error")

    def emit_binary(self, path: str):
        ModifyBinary(self.module, self.module.path).emit_binary(path)
    def get_flat_instrs(self, instrs):
        ret_instrs = []
        for _, i in enumerate(instrs):
            if i.opcode in [Block, Loop]:
                ret_instrs.append(i)
                args = i.args
                ret_instrs.extend(self.get_flat_instrs(args.instrs))
                ret_instrs.append(Instruction(End_))
            elif i.opcode == If:
                ret_instrs.append(i)
                args = i.args
                ret_instrs.extend(self.get_flat_instrs(args.instrs1))
                ret_instrs.append(Instruction(Else_))
                ret_instrs.extend(self.get_flat_instrs(args.instrs2))
                ret_instrs.append(Instruction(End_))
            else:
                ret_instrs.append(i)
        return ret_instrs

    def get_fold_instrs(self, instrs):
        ret_instrs = []
        i = 0
        while i < len(instrs):
            if instrs[i].opcode in [Block, Loop]:
                j = i
                args_instrs_length = self.get_flat_Block_length(instrs[i:]) - 2
                instrs[i].args.instrs = self.get_fold_instrs(instrs[i + 1: i + 1 + args_instrs_length])
                i = i + args_instrs_length + 2
                ret_instrs.append(instrs[j])
            elif instrs[i].opcode == If:
                j = i
                else_offset, length = self.get_flat_If_length(instrs[i:]) - 2
                instrs[j].args.instrs1 = self.get_fold_instrs(instrs[i + 1, i + else_offset])
                i = i + else_offset
                instrs[j].args.instrs2 = self.get_fold_instrs(instrs[i + 1, i + length - 1])
                i = j + length
                ret_instrs.append(instrs[j])
            else:
                ret_instrs.append(instrs[i])
                i += 1
        return ret_instrs

    def get_flat_Block_length(self, instrs):

        if instrs[0].opcode in [Block, Loop]:
            instr_queue = [instrs[0]]
            i = 1
            while i < len(instrs):
                if instrs[i].opcode in [Block, Loop]:
                    instr_queue.append(instrs[i])
                    i += 1
                elif instrs[i].opcode in [If, Else_]:
                    instr_queue.append(instrs[i])
                    i += 1
                elif instrs[i].opcode == End_:
                    instr_queue.append(instrs[i])
                    i += 1
                    if instr_queue[-2].opcode == Else_:
                        instr_queue = instr_queue[0: -3]
                    elif instr_queue[-2].opcode in [Block, Loop]:
                        instr_queue = instr_queue[0: -2]
                    if instr_queue == []:
                        length = i
                        return length
                else:
                    i += 1
        else:
            raise Exception("error")

    def get_flat_If_length(self, instrs):

        if instrs[0].opcode in [If]:
            instr_queue = [{
                        "offset": 0,
                        "instr": instrs[0]
                    }]
            i = 1
            while i < len(instrs):
                if instrs[i].opcode in [Block, Loop]:
                    instr_queue.append({
                        "offset": i,
                        "instr": instrs[i]
                    })
                    i += 1
                elif instrs[i].opcode in [If, Else_]:
                    instr_queue.append({
                        "offset": i,
                        "instr": instrs[i]
                    })
                    i += 1
                elif instrs[i].opcode == End_:
                    instr_queue.append({
                        "offset": i,
                        "instr": instrs[i]
                    })
                    i += 1
                    if instr_queue[-2].opcode == Else_ and len(instr_queue) != 3:
                        instr_queue = instr_queue[0: -3]
                    elif instr_queue[-2].opcode in [Block, Loop]:
                        instr_queue = instr_queue[0: -2]
                    elif instr_queue[-2].opcode == Else_ and len(instr_queue) == 3:
                        else_offset = instr_queue[1]["offset"]
                        length = i
                        return else_offset, length
                else:
                    i += 1
        else:
            raise Exception("error")
