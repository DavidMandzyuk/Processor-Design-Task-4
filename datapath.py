"""
datapath.py

Single-Cycle Datapath for the 32-bit Processor.

Wires together:
  - InstructionDecoder
  - ControlUnit
  - RegisterFile
  - ALU
  - RegDstMux

Pipeline stages (all in one clock cycle):
  1. Fetch - load instruction word from the program.
  2. Decode - InstructionDecoder + ControlUnit produce fields & signals.
  3. Execute - RegisterFile reads; ALU computes.
  4. Write-back - RegisterFile writes result (if reg_write=1).
"""

from register_file import RegisterFile
from alu import ALU
from instruction import InstructionDecoder
from control_unit import ControlUnit
from mux import RegDstMux
from dataclasses import dataclass, field
from typing import Any


@dataclass
class CycleTrace:
    # Complete trace of one instruction's execution.
    pc: int
    instruction_hex: str
    mnemonic: str
    # Decode
    opcode: int
    rs: int
    rt: int
    rd: int
    funct: int
    # Control
    control_signals: dict
    # Execute
    operand_a: int
    operand_b: int
    alu_result: int
    # Write-back
    dest_reg: int
    dest_reg_name: str
    reg_written: bool
    # Register snapshot after instruction
    registers_after: dict = field(default_factory=dict)


class Datapath:
    """
    Models the complete single-cycle datapath.

    Usage
    -----
        dp = Datapath()
        dp.load_registers({'t0': A, 't1': B, 't2': C, 't3': D, 't5': C})
        traces = dp.run(program)
    """

    REG_NAMES = [f"t{i}" for i in range(8)]

    def __init__(self):
        self.reg_file    = RegisterFile()
        self.alu         = ALU()
        self.decoder     = InstructionDecoder()
        self.ctrl        = ControlUnit()
        self.reg_dst_mux = RegDstMux()
        self.pc          = 0

    def load_registers(self, values: dict) -> None:
        """Pre-load register values by name."""
        self.reg_file.load_values(values)

    def run(self, program: list) -> list:
        """
        Execute the list of 32-bit instruction words.

        Returns a list of CycleTrace objects (one per instruction).
        """
        traces = []
        for idx, instr_word in enumerate(program):
            trace = self._execute_one(idx, instr_word)
            traces.append(trace)
        return traces

    # ------------------------------------------------------------------
    # Internal – one instruction cycle
    # ------------------------------------------------------------------

    def _execute_one(self, pc: int, instr_word: int) -> CycleTrace:
        # ── Stage 1: Fetch ───────────────────────────────────────────
        # (In a real processor the PC would index instruction memory;
        #  here we receive the word directly.)

        # ── Stage 2: Decode ──────────────────────────────────────────
        decoded  = self.decoder.decode(instr_word)
        signals  = self.ctrl.generate(decoded)

        # ── Stage 3: Execute ─────────────────────────────────────────
        # Register reads
        operand_a = self.reg_file.read(decoded.rs)
        operand_b = self.reg_file.read(decoded.rt)

        # RegDst MUX: choose destination register
        dest_reg = self.reg_dst_mux.get_dest_reg(
            rt=decoded.rt,
            rd=decoded.rd,
            mux_reg_dst=signals.mux_reg_dst,
        )

        # ALU
        alu_out = self.alu.execute(
            input_a  = operand_a,
            input_b  = operand_b,
            alu_op   = signals.alu_op,
            invert_a = signals.invert_a,
        )

        # ── Stage 4: Write-back ──────────────────────────────────────
        self.reg_file.write(dest_reg, alu_out["result"], signals.reg_write)

        return CycleTrace(
            pc              = pc,
            instruction_hex = f"0x{instr_word:08X}",
            mnemonic        = decoded.mnemonic,
            opcode          = decoded.opcode,
            rs              = decoded.rs,
            rt              = decoded.rt,
            rd              = decoded.rd,
            funct           = decoded.funct,
            control_signals = signals.as_dict(),
            operand_a       = operand_a,
            operand_b       = operand_b,
            alu_result      = alu_out["result"],
            dest_reg        = dest_reg,
            dest_reg_name   = self.REG_NAMES[dest_reg],
            reg_written     = signals.reg_write,
            registers_after = self.reg_file.dump(),
        )
