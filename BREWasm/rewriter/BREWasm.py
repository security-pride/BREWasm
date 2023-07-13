from BREWasm.rewriter.modify_binary import ModifyBinary


class BREWasm:

    def __init__(self, path: str):
        self.path = path
        self.module = ModifyBinary(path).module

    def emit_binary(self, path):
        ModifyBinary(self.path, module=self.module).emit_binary(path)
