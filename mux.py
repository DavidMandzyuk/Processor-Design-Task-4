"""
mux.py

MUX components for the Single-Cycle 32-bit Processor.

Provided MUX classes:
  Mux2to1 - selects between two inputs based on a 1-bit select line.
  RegDstMux - selects destination register.
"""


class Mux2to1:
    # select = 0 -> output = input_0
    # select = 1 -> output = input_1
    def select(self, input_0, input_1, sel: int):
        if sel not in (0, 1):
            raise ValueError(f"Mux2to1: select must be 0 or 1, got {sel}")
        return input_1 if sel else input_0


class RegDstMux(Mux2to1):
    """
    Chooses which instruction field supplies the write-register index.
      sel = 0 -> rt (I-type destination)
      sel = 1 -> rd (R-type destination)
    """

    def get_dest_reg(self, rt: int, rd: int, mux_reg_dst: bool) -> int:
        return self.select(rt, rd, int(mux_reg_dst))
