************
Section Rewriter API
************


Constants
===================

.. data:: I32

   32-bit integer type.

.. data:: I64

   64-bit integer type.

.. data:: F32

   32-bit floating point type.

.. data:: F64

   64-bit floating point type.



Section Rewriter class
===================

SectionRewriter
-----

.. class:: SectionRewriter(module, **section)

   Attributes:

   .. attribute:: module

      The Wasm module to be rewrited.

   .. attribute:: section
      
      The Wasm section to be rewrited. It receives a dictionary as input, such as ``SectionRewriter(module, typesec=module.typesec)``. The optional keys are as follows:
      
      * typesec 
      * importsec
      * funcsec
      * tablesec
      * memsec
      * globalsec
      * exportsec
      * startsec
      * elemsec
      * codesec
      * datasec
      * customsec
         

   .. function:: select(query) -> list:

      Select elements in the section by condition *query*.

      :param query: The query to select element objects.
      :type query: Query are represented by the element in each section, such as ``Global(globalidx=1)``. If query is passed by ``None``, the function will return all elements in corresponding section.

      :returns: A list of section element objects.
      :rtype: list


   .. function:: insert(query, inserted_item):

      Insert a element in the section by condition *query*.

      :param query: The query to the location of the element to be inserted.
      :type query: Query are represented by the element in each section, such as ``Global(globalidx=1)``. If you passed ``None``, it equals to append operation, which means a new item will be appended at end of the section.

      :param inserted_item: The element to be inserted.
      :type inserted_item: There is no need to specify the index of the inserted element because it has already been identified by the param *query*.

   .. function:: update(query, new_item):

      Update a element in the section by condition *query*.

      :param query: The query to the location of the element to be updated.
      :type query: As function *insert*.

      :param new_item: The new element.
      :type new_item: If you only want to update a certain property, you don't need to specify other irrelevant parameters. For example, ``Type(arg_types=[I32, I64])``

   .. function:: delete(query):

      Delete a element in the section by condition *query*.

      :param query: The query to the location of the element to be deleted.
      :type query: As function *insert*.



Section element classes
===================

Type section
-----

.. class:: Type(typeidx, arg_types, ret_types)
   
   Attributes:

   .. attribute:: typeidx

      The index of the element in the section (``int``).

   .. attribute:: arg_types
      
      The argument of the type. Example: ```arg_types=[I32, F32]```

   .. attribute:: ret_types

      The return of the type. Example: ```ret_types=[I32, F32]```


Import section
-----

.. class:: Import(importidx, module, name, typeidx)
   
   Attributes:

   .. attribute:: importidx

      The index of the element in the section.

   .. attribute:: module

      The module name of the import elment. Example: ```module="wasi"```

   .. attribute:: name

      The name of the import element. Example: ```name="fd_write"```
   
   .. attribute:: typeidx

      The index of the function type (``int``).

Function section
-----

.. class:: Function(funcidx, typeidx)
   
   Attributes:

   .. attribute:: funcidx

      The index of the element in the section (``int``).

   .. attribute:: typeidx

      The index of the function type (``int``).


Table section
-----

.. class:: Table(min, max)
   
   Attributes:

   .. attribute:: min

      Specifies a limit on the number of elements. The required lower limit (``int``).

   .. attribute:: max

      The optional upper (``int``).

Memory section
-----

.. class:: Memory(min, max)
   
   Attributes:

   .. attribute:: min

      The required Minimum pages of the linear memory (``int``).

   .. attribute:: max

      The optional maximum pages (``int``).

Global section
-----

.. class:: Global(globalidx, valtype, mut, val)
   
   Attributes:

   .. attribute:: globalidx

      The index of the element in the section (``int``).

   .. attribute:: valtype

      The value type of the global variable. Example: ```valtype=I32```

   .. attribute:: mut

      The mutable of the global variable. Mutable is ``1``, immutable is ``0``.
   
   .. attribute:: val

      The initial value of the global variable.


Export section
-----

.. class:: Export(exportidx, name, funcidx)
   
   Attributes:

   .. attribute:: exportidx

      The index of the element in the section (``int``).

   .. attribute:: name

      The name of the export function.

   .. attribute:: funcidx

      The index of the exported function.
   

Start section
-----

Element section
-----

.. class:: Element(elemidx, tableidx, offset, funcidx_list)
   
   Attributes:

   .. attribute:: elemidx

      The index of the element in the section (``int``).

   .. attribute:: tableidx

      The table which this element belongs. Its value is fixed at ``1``.

   .. attribute:: offset

      The offset of the *funcidx_list* in final indirect function table (``int``).

   .. attribute:: funcidx_list

      The function indices of the indirect function table.


Code section
-----

.. class:: Code(funcidx, local_vec, instr_list)
   
   Attributes:

   .. attribute:: funcidx

      The index of the element in the section (``int``).

   .. attribute:: local_vec

      The name of the export function (`Local`). Note that all local variables should be indexed from 0.

   .. attribute:: instr_list

      The function body.

   .. note::
      
      There is no need to consider the nest relation of instructions. Just flatten all the instructions. For example, ``[Instruction(Block), Instruction(I32Const, 1), Instruction(Drop), Instruction(End)]``

.. class:: Local(localidx, valtype)

   Attributes:

   .. attribute:: localidx

      The index of this local variable (`int`).

   .. attribute:: valtype

      The value type of this local variable


Data section
-----

.. class:: Data(dataidx, offset, init_data)
   
   Attributes:

   .. attribute:: dataidx

      The index of the element in the section (``int``).

   .. attribute:: offset

      The offset of the *init_data* in final Linear memory(``int``).

   .. attribute:: init_data

      The initial bytes of this data (``bytes``).

Custom section
-----

.. class:: CustomName(name_type, idx, name)
   
   Attributes:

   .. attribute:: name_type

      The type of the debug name. The preset types are as follows: 

      * FunctionName
      * GlobalName
      * DataName

   .. attribute:: idx

      The index of the debug name.

   .. attribute:: name

      The debug name (``str``).      


Instruction classes
===================

Instruction
-----

.. class:: Instruction(opcode, args)

   The type of the args depends on the opcode:
   * If the *opcode* are control instruction such as Block and Loop. *args* must be `None`
   * Most of the other instructions only need constant argument.

   Attributes:

   .. attribute:: opcode

      Operation code (int). BREWasm has pre-defined the instruction constants, as follows:

      .. code-block:: python

         Unreachable = 0x00
         Nop = 0x01
         Block = 0x02
         Loop = 0x03
         If = 0x04
         Else_ = 0x05
         End_ = 0x0B
         Br = 0x0C
         BrIf = 0x0D
         BrTable = 0x0E
         Return = 0x0F
         Call = 0x10
         CallIndirect = 0x11
         Drop = 0x1A
         Select = 0x1B
         LocalGet = 0x20
         LocalSet = 0x21
         LocalTee = 0x22
         GlobalGet = 0x23
         GlobalSet = 0x24
         I32Load = 0x28
         I64Load = 0x29
         F32Load = 0x2A
         F64Load = 0x2B
         I32Load8S = 0x2C
         I32Load8U = 0x2D
         I32Load16S = 0x2E
         I32Load16U = 0x2F
         I64Load8S = 0x30
         I64Load8U = 0x31
         I64Load16S = 0x32
         I64Load16U = 0x33
         I64Load32S = 0x34
         I64Load32U = 0x35
         I32Store = 0x36
         I64Store = 0x37
         F32Store = 0x38
         F64Store = 0x39
         I32Store8 = 0x3A
         I32Store16 = 0x3B
         I64Store8 = 0x3C
         I64Store16 = 0x3D
         I64Store32 = 0x3E
         MemorySize = 0x3F
         MemoryGrow = 0x40
         I32Const = 0x41
         I64Const = 0x42
         F32Const = 0x43
         F64Const = 0x44
         I32Eqz = 0x45
         I32Eq = 0x46
         I32Ne = 0x47
         I32LtS = 0x48
         I32LtU = 0x49
         I32GtS = 0x4A
         I32GtU = 0x4B
         I32LeS = 0x4C
         I32LeU = 0x4D
         I32GeS = 0x4E
         I32GeU = 0x4F
         I64Eqz = 0x50
         I64Eq = 0x51
         I64Ne = 0x52
         I64LtS = 0x53
         I64LtU = 0x54
         I64GtS = 0x55
         I64GtU = 0x56
         I64LeS = 0x57
         I64LeU = 0x58
         I64GeS = 0x59
         I64GeU = 0x5A
         F32Eq = 0x5B
         F32Ne = 0x5C
         F32Lt = 0x5D
         F32Gt = 0x5E
         F32Le = 0x5F
         F32Ge = 0x60
         F64Eq = 0x61
         F64Ne = 0x62
         F64Lt = 0x63
         F64Gt = 0x64
         F64Le = 0x65
         F64Ge = 0x66
         I32Clz = 0x67
         I32Ctz = 0x68
         I32PopCnt = 0x69
         I32Add = 0x6A
         I32Sub = 0x6B
         I32Mul = 0x6C
         I32DivS = 0x6D
         I32DivU = 0x6E
         I32RemS = 0x6F
         I32RemU = 0x70
         I32And = 0x71
         I32Or = 0x72
         I32Xor = 0x73
         I32Shl = 0x74
         I32ShrS = 0x75
         I32ShrU = 0x76
         I32Rotl = 0x77
         I32Rotr = 0x78
         I64Clz = 0x79
         I64Ctz = 0x7A
         I64PopCnt = 0x7B
         I64Add = 0x7C
         I64Sub = 0x7D
         I64Mul = 0x7E
         I64DivS = 0x7F
         I64DivU = 0x80
         I64RemS = 0x81
         I64RemU = 0x82
         I64And = 0x83
         I64Or = 0x84
         I64Xor = 0x85
         I64Shl = 0x86
         I64ShrS = 0x87
         I64ShrU = 0x88
         I64Rotl = 0x89
         I64Rotr = 0x8A
         F32Abs = 0x8B
         F32Neg = 0x8C
         F32Ceil = 0x8D
         F32Floor = 0x8E
         F32Trunc = 0x8F
         F32Nearest = 0x90
         F32Sqrt = 0x91
         F32Add = 0x92
         F32Sub = 0x93
         F32Mul = 0x94
         F32Div = 0x95
         F32Min = 0x96
         F32Max = 0x97
         F32CopySign = 0x98
         F32CopySign = 0x98
         F64Abs = 0x99
         F64Neg = 0x9A
         F64Ceil = 0x9B
         F64Floor = 0x9C
         F64Trunc = 0x9D
         F64Nearest = 0x9E
         F64Sqrt = 0x9F
         F64Add = 0xA0
         F64Sub = 0xA1
         F64Mul = 0xA2
         F64Div = 0xA3
         F64Min = 0xA4
         F64Max = 0xA5
         F64CopySign = 0xA6
         I32WrapI64 = 0xA7
         I32TruncF32S = 0xA8
         I32TruncF32U = 0xA9
         I32TruncF64S = 0xAA
         I32TruncF64U = 0xAB
         I64ExtendI32S = 0xAC
         I64ExtendI32U = 0xAD
         I64TruncF32S = 0xAE
         I64TruncF32U = 0xAF
         I64TruncF64S = 0xB0
         I64TruncF64U = 0xB1
         F32ConvertI32S = 0xB2
         F32ConvertI32U = 0xB3
         F32ConvertI64S = 0xB4
         F32ConvertI64U = 0xB5
         F32DemoteF64 = 0xB6
         F64ConvertI32S = 0xB7
         F64ConvertI32U = 0xB8
         F64ConvertI64S = 0xB9
         F64ConvertI64U = 0xBA
         F64PromoteF32 = 0xBB
         I32ReinterpretF32 = 0xBC
         I64ReinterpretF64 = 0xBD
         F32ReinterpretI32 = 0xBE
         F64ReinterpretI64 = 0xBF
         I32Extend8S = 0xC0
         I32Extend16S = 0xC1
         I64Extend8S = 0xC2
         I64Extend16S = 0xC3
         I64Extend32S = 0xC4
         TruncSat = 0xFC


   .. attribute:: args

      Operand (``int``) or ``None``
