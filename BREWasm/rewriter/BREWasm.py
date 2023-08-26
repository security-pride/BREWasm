from BREWasm.rewriter.modify_binary import ModifyBinary


class BREWasm:

    def __init__(self, path):
        self.path = path
        self.module = ModifyBinary(module=None, path=path).module

    def emit_binary(self, path):
        ModifyBinary(path=self.path, module=self.module).emit_binary(path)
