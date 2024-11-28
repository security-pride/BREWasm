**************
BREWasm Usage
**************

Installation
============

Install BREWasm::

    python3 -m pip install BREWasm

``BREWasm`` requires Python 3.10 or newer.


Usage
===========

Section Rewriter
-----------------

The basic operation of the section rewriter is ``select``, ``insert``, ``update`` and ``delete``.::

    from BREWasm import *

    binary = BREWasm('a.wasm')  # Open a Wasm binary file

    # Initialize a section rewriter of the global section. 
    global_rewriter = SectionRewriter(binary.module, globalsec=binary.module.global_sec)

    # Select all the items in global section
    global_list = global_rewriter.select(Global())
    # Get the attribute globalidx of a global item, whose index is one.
    idx = global_list[1].globalidx
    # Insert a new global item at the index idx of the global section
    global_rewriter.insert(Global(idx), Global(valtype=ValTypeI32, val=100))
    # Delete the global item whose index is idx.
    global_rewriter.delete(Global(idx))
    # Emit a new binary file
    binary.emit_binary('b.wasm')



Semantics Rewriter
-----------------

Insert a internal function in the binary

    from BREWasm import *

    binary = BREWasm('a.wasm') # Open a Wasm binary file

    # Initialize a semantics rewriter of the function semantics
    function_rewriter = SemanticsRewriter.Function(binary.module)
    # Define the instructions of function
    func_body = [Instruction(LocalGet, 0), Instruction(LocalGet, 1), Instruction(I32Add, 0), Instruction(Nop)]
    # Insert a internal function in the binary
    function_rewriter.insert_internal_function(idx=1, params_type=[ValTypeI32, ValTypeI32], results_type=[ValTypeI32], local_vec=[Local(0, ValTypeI32), Local(1, ValTypeI64)], func_body=func_body)
    # Emit a new binary file
    binary.emit_binary('b.wasm')


.. note::
   Instructions are only indented for readability.
