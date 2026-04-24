"""
alu.py

ALU for the Single-Cycle 32-bit Processor.

Supported operations:
  - AND (0b00): result = A & B
  - OR (0b01): result = A | B

Inversion flag (invert_a):
  - When True, input A is bitwise-inverted before the operation.
  - This implements NOT without a dedicated instruction (e.g., ~C & D).
"""

from enum import IntEnum


class ALUOp(IntEnum):
    AND = 0b00
    OR = 0b01


class ALU:
    MASK_32 = 0xFFFFFFFF

    def execute(
        self,
        input_a: int,
        input_b: int,
        alu_op: ALUOp,
        invert_a: bool = False,
    ) -> dict:
        
        """
        Performs the ALU operation and returns a result dictionary.

        Parameters:
        input_a: int - first operand (32-bit)
        input_b: int - second operand (32-bit)
        alu_op: ALUOp - operation selector
        invert_a: bool - if True, bitwise-invert input_a before operation

        Returns:
        dict with keys:
          'result' - 32-bit output
          'input_a_raw' - input_a before inversion
          'input_a_eff' - effective input_a (after optional inversion)
          'input_b' - input_b (unchanged)
          'alu_op' - operation performed
          'invert_a' - inversion flag used
        """

        a_raw = input_a & self.MASK_32
        b = input_b & self.MASK_32

        # Applies optional inversion on input A.
        a_eff = (~a_raw) & self.MASK_32 if invert_a else a_raw

        if alu_op == ALUOp.AND:
            result = a_eff & b
        elif alu_op == ALUOp.OR:
            result = a_eff | b
        else:
            raise ValueError(f"Unsupported ALUOp: {alu_op!r}")

        return {
            "result": result & self.MASK_32,
            "input_a_raw": a_raw,
            "input_a_eff": a_eff,
            "input_b": b,
            "alu_op": alu_op,
            "invert_a": invert_a,
        }

    # Convenience wrappers
    def and_op(self, a: int, b: int) -> int:
        return self.execute(a, b, ALUOp.AND)["result"]

    def or_op(self, a: int, b: int) -> int:
        return self.execute(a, b, ALUOp.OR)["result"]

    def and_not_a(self, a: int, b: int) -> int:
        # Computes (~A) & B
        return self.execute(a, b, ALUOp.AND, invert_a=True)["result"]
