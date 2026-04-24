"""
control_unit.py

Control Unit for the Single-Cycle 32-bit Processor.

Responsibilities:
    - Receive the decoded instruction (opcode + funct).
    - Generate all control signals required by the datapath.

Control signals produced:
    reg_write:      1 -> write result to destination register
    alu_op:         ALUOp enum  (AND / OR)
    invert_a:       1 -> invert ALU input A before operation
    mux_reg_dst:    Always 1 for R-type
"""

from dataclasses import dataclass
from alu import ALUOp
from instruction import (
    DecodedInstruction,
    OPCODE_RTYPE,
    FUNCT_AND,
    FUNCT_OR,
    FUNCT_AND_NOT_A,
)


@dataclass
class ControlSignals:
    reg_write: bool
    alu_op: ALUOp
    invert_a: bool
    mux_reg_dst: bool

    def as_dict(self) -> dict:
        return {
            "reg_write": int(self.reg_write),
            "alu_op": self.alu_op.name,
            "invert_a": int(self.invert_a),
            "mux_reg_dst": int(self.mux_reg_dst),
        }

    def __str__(self) -> str:
        d = self.as_dict()
        return (
            f"reg_write={d['reg_write']}  "
            f"alu_op={d['alu_op']:<3}  "
            f"invert_a={d['invert_a']}  "
            f"mux_reg_dst={d['mux_reg_dst']}"
        )


class ControlUnit:
    # Given a DecodedInstruction, returns the appropriate ControlSignals.

    # funct -> (ALUOp, invert_a)
    _FUNCT_SIGNALS = {
        FUNCT_AND: (ALUOp.AND, False),
        FUNCT_OR: (ALUOp.OR,  False),
        FUNCT_AND_NOT_A: (ALUOp.AND, True),
    }

    def generate(self, decoded: DecodedInstruction) -> ControlSignals:
        # Decodes the instruction and produces control signals.

        # Raises ValueError for unsupported opcodes or funct codes.
        if decoded.opcode != OPCODE_RTYPE:
            raise ValueError(
                f"ControlUnit: unsupported opcode {decoded.opcode:#010b}"
            )

        if decoded.funct not in self._FUNCT_SIGNALS:
            raise ValueError(
                f"ControlUnit: unknown funct field {decoded.funct:#08b}"
            )

        alu_op, invert_a = self._FUNCT_SIGNALS[decoded.funct]

        return ControlSignals(
            reg_write = True,
            alu_op = alu_op,
            invert_a = invert_a,
            mux_reg_dst = True,
        )
