************
Semantics Rewriter API
************


Semantics Rewriter class
===================

SectionRewriter
-----

.. class:: SectionRewriter(module)

   Attributes:

   .. attribute:: module

      The Wasm module to be rewrited.


Global Variable
-----

   .. function:: appendGlobalVariable (global_type, init_value):

      Append a global variable.

      :param global_type: The type of the global variable. Value type:

      * I32
      * I64
      * F32
      * F64

      :param init_value: The initial value of the global variable (`int` or `float`).


   .. function:: modifyGlobalVariable (idx, global_type, init_value):

      Modify a global variable.

      :param idx: The index of the global variable to be modified.
      
      :param global_type: The type of the new global variable. Refer to *appendGlobalVariable*

      :param init_value: The initial value of the new global variable (`int` or `float`).

   .. function:: deleteGlobalVariable (idx=None, global_type=None, init_value=None):

      Delete a global variable.

      :param idx: The index of the global variable to be deleted.
      
      :param global_type: The type of the global variable to be deleted. Refer to *appendGlobalVariable*

      :param init_value: The initial value of the global variable to be deleted. (`int` or `float`).

   .. note::
      There are two methods to delete the global variable. The one is to specify the index of the global variable to be deleted. The other one is to specify the tangible attributes.


   .. function:: insertGlobalVariable (idx, global_type, init_value):

      Insert a global variable.

      :param idx: The index of the global variable to be inserted.
      
      :param global_type: The type of the global variable to be inserted. Refer to *appendGlobalVariable*

      :param init_value: The initial value of the global variable to be inserted. (`int` or `float`).


Import & Export
-----

    .. function:: insertImportFunction  (idx, module_name, func_name, params_type, results_type):

      Insert a import function.

      :param idx: The index of the global variable to be inserted.
      
      :param module_name: The module name of the import function to be inserted (`str`).

      :param func_name: The function name of the import function to be inserted (`str`).

      :param params_type: The parameters type of the function. For example, `params_type=[I32, I64]`.

      :param results_type: The return value type of the function. For example, `results_type=[F32, I64]`.

   .. function:: appendImportFunction  (module_name, func_name, params_type, results_type):

      Append a import function.

      :param module_name: Similar to *insertImportFunction*

      :param func_name: Similar to *insertImportFunction*

      :param params_type: Similar to *insertImportFunction*

      :param results_type: Similar to *insertImportFunction*

   .. function:: modifyImportFunction  (idx, module_name, func_name, params_type, results_type):

      Modify a import function.

      :param idx: Similar to *insertImportFunction*

      :param module_name: Similar to *insertImportFunction*

      :param func_name: Similar to *insertImportFunction*

      :param params_type: Similar to *insertImportFunction*

      :param results_type: Similar to *insertImportFunction*

   .. function:: deleteImportFunction (idx=None, module_name=None, func_name=None):

      Delete a import function.

      :param idx: Similar to *insertImportFunction*

      :param module_name: Similar to *insertImportFunction*

      :param func_name: Similar to *insertImportFunction*
   
   .. note::

      It can be deleted by index or names.

    
    .. function:: insertExportFunction   (idx, func_name, funcidx):

      Insert a export function.

      :param idx: The index of the export function to be inserted.

      :param func_name: The export function name.

      :param funcidx: The index of the internal function to be exported.


   .. function:: appendExportFunction   (func_name, funcidx):

      Append a export function.

      :param func_name: Similar to *insertExportFunction*

      :param funcidx: Similar to *insertExportFunction*


   .. function:: modifyExportFunction   (idx, func_name, funcidx):

      Modify a export function

      :param idx: Similar to *insertExportFunction*

      :param func_name: Similar to *insertExportFunction*

      :param funcidx: Similar to *insertExportFunction*


   .. function:: deleteExportFunction  (idx=None, func_name=None):

      Delete a export function. Similar to *deleteGlobalVariable*.

      :param idx: Similar to *insertExportFunction*

      :param func_name: Similar to *insertExportFunction*


Linear Memory
-----

   .. function:: appendLinearMemory  (offset, bytes):

      Appends an initialized data at the specified offset in linear memory.

      :param offset: The offset of the data to be appended (`int`).

      :param bytes: Initial data (`bytes`).


   .. function:: modifyLinearMemory  (offset, bytes):

      Modify the initial data of the linear memory at specified offset.

      :param offset: Similar to *appendLinearMemory*.

      :param bytes: Similar to *appendLinearMemory*.


Function
-----

   .. function:: insertInternalFunction   (idx, params_type, results_type, local_vec, func_body):

      Insert a internal function.

      :param idx: The index of the function to be inserted.

      :param params_type: The function parameters type. Similar to *insertImportFunction*

      :param results_type: The function return values type. Similar to *insertImportFunction*

      :param local_vec: The local variable of the function (`Local`). Note that all local variables should be indexed from 0.

      :param func_body: The function body.

   example::

      .. code-block:: python
         
         # Initialize a semantics rewriter of the function semantics
         function_rewriter = SemanticRewriter.Function(binary)
         # Define the instructions of function
         funcbody = [Instruction(LocalGet, 0), Instruction(LocalGet, 1), Instruction(I32Add, 0), Instruction(Nop)]
         # Insert a internal function in the binary
         function_rewriter.insert_internal_function(idx=1, params_type=[I32, I32], results_type=[I32], local_vec=[Local(0, I32), Local(1, I64)], funcbody)


   .. function:: insertIndirectFunction   (idx, params_type, results_type, local_vec, func_body):

      Insert a indirect function.

      :param idx: The index of the function to be inserted.

      :param params_type: The function parameters type. Similar to *insertImportFunction*

      :param results_type: The function return values type. Similar to *insertImportFunction*

      :param local_vec: The local variable of the function (`Local`). Note that all local variables should be indexed from 0.

      :param func_body: The function body.

   .. function:: insertHookFunction   (hooked_funcidx, idx, params_type, results_type, locals_vec, func_body):

      Insert a indirect function.

      :param hooked_funcidx: The index of the hooked function.

      :param idx: The index of the hook function to be inserted.

      :param params_type: The function parameters type. Similar to *insertImportFunction*

      :param results_type: The function return values type. Similar to *insertImportFunction*

      :param local_vec: The local variable of the function (`Local`). Note that all local variables should be indexed from 0.

      :param func_body: The function body.

   .. function:: deleteFuncInstr   (funcidx, offset):

      Delete a instruction of a function by offset.

      :param funcidx: The function index of the instruction to be deleted.

      :param offset: The flattening offset of an instruction in a function.

   .. note::

      There is no need to consider the nest relation of instructions. Just flatten all the instructions. For example, ``[Instruction(Block), Instruction(I32Const, 1), Instruction(Drop), Instruction(End)]``. The offset of the `Drop` is 2.

    
    .. function:: appendFuncInstrs    (funcidx, instrs: list):

      Append a list of instructions to an internal function.

      :param funcidx: The function index.

      :param instrs: The instruction list. For example, ``[Instruction(Block), Instruction(I32Const, 1), Instruction(Drop), Instruction(End)]``.


   .. function:: insertFuncInstrs    (funcidx, offset, instrs: list):

      Insert a list of instructions to an internal function.

      :param funcidx: The function index.

      :param offset: The offset of the instrunctions to be inserted.

      :param instrs: The instruction list. For example, ``[Instruction(Block), Instruction(I32Const, 1), Instruction(Drop), Instruction(End)]``.

   .. function:: modifyFuncInstr   (funcidx, instr, instrs: list):

      Modify all the specified instructions of an internal function with instructions. This function enables batch replacement of instructions in functions.

      :param funcidx: The function index.

      :param instr: The specified instruction to be replaced.

      :param instrs: The instruction list. For example, ``[Instruction(Block), Instruction(I32Const, 1), Instruction(Drop), Instruction(End)]``.

   .. function:: appendFuncLocal  (funcidx, valtype):

      Append a local variable for a function.

      :param funcidx: The function index.

      :param valtype: The value type of the local variable to be appended.

Custom Content
-----

    .. function:: modifyFuncName    (funcidx, name):

      Modify the function debug name.

      :param funcidx: The function index.

      :param name: The debug name.


   .. function:: deleteFuncName    (funcidx):

      Delete the function debug name.

      :param funcidx: The function index.

   .. function:: insertFuncName    (funcidx, name):

      Insert a function debug name.

      :param funcidx: The function index.
      
      :param name: The debug name.

   .. function:: modifyGlobalName    (globalidx, name):

      Modify the debug name of a global variable.

      :param globalidx: The index of the global variable.

      :param name: The debug name.

    
    .. function:: deleteGlobalName     (globalidx):

      Delete the debug name of a global variable.

      :param globalidx: The index of the global variable.


   .. function:: insertGlobalName     (globalidx, name):

      Insert a debug name for a global variable.

      :param globalidx: The index of the global variable.

      :param name: The debug name.

   .. function:: insertDataName    (dataidx, name):

      Insert a debug name for a linear memory.

      :param dataidx: The index of the data.

      :param name: The debug name.

   .. function:: modifyDataName   (dataidx, name):

      Modify the debug name of a linear memory.

      :param dataidx: The index of the data.

      :param name: The new debug name.

   .. function:: deleteDataName    (dataidx):

      Delete the debug name of a linear memory.

      :param dataidx: The index of the data.
