from ..parser.opnames import opnames


class Expr(list):

    def __init__(self):
        super().__init__()


class Instruction:

    def __init__(self, opcode=None, args=None):
        self.opcode = opcode

        self.args = args

    def get_opname(self):
        return opnames[self.opcode]

    def __str__(self):
        return opnames[self.opcode]


class BlockArgs:

    def __init__(self, bt=None, instrs=None):
        self.bt = bt

        self.instrs = instrs


class IfArgs:

    def __init__(self):
        self.bt = None
        self.instrs1 = []
        self.instrs2 = []


class BrTableArgs:

    def __init__(self, labels=None, default=None):
        if labels is None:
            labels = []
        self.labels = labels

        self.default = default


class MemArg:

    def __init__(self, align=0, offset=0):
        self.align = align

        self.offset = offset

class TableArg:

    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y


class MemLaneArg:

    def __init__(self, mem_arg=None, laneidx=0):
        self.mem_arg = mem_arg
        self.laneidx = laneidx