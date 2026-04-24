"""
instruction.py

Instruction encoding / decoding for the Single-Cycle 32-bit Processor.

32-bit R-Type instruction layout:
 31      26  25    21  20    16  15    11  10     6  5          0
 [ opcode ]  [  rs  ]  [  rt  ]  [  rd  ]  [ shamt ]  [  funct  ]
   6 bits      5 bits    5 bits    5 bits    5 bits      6 bits

Field definitions:
  opcode: 000000  (all R-type instructions share opcode 0)
  rs: source register 1  (first operand)
  rt: source register 2  (second operand)
  rd: destination register
  shamt: shift amount — unused (0)
  funct: encodes operation + inversion flag

Function field encoding:
  [5] = invert_a (1 = invert input rs before operation)
  [4:0] = base_op
    - 00001 -> AND (standard)
    - 00010 -> OR
"""

from dataclasses import dataclass
from alu import ALUOp


# Function-field constants
FUNCT_AND = 0b000001   
#1 – standard AND
FUNCT_OR = 0b000010   
#2 – standard OR
FUNCT_AND_NOT_A = 0b100001   
#33 – AND with invert-A (implements ~rs & rt)
OPCODE_RTYPE = 0b000000


@dataclass
class DecodedInstruction:
    # Fully decoded fields of a single instruction.
    raw: int   # original 32-bit word
    opcode: int
    rs: int   # source register 1 index
    rt: int   # source register 2 index
    rd: int   # destination register index
    shamt: int
    funct: int
    alu_op: ALUOp
    invert_a: bool
    mnemonic: str


class InstructionDecoder:
    # Decodes a 32-bit instruction word into its individual fields and derive the control signals needed by the ALU.
    
    # Map function
    _FUNCT_TABLE = {
        FUNCT_AND: (ALUOp.AND, False),
        FUNCT_OR: (ALUOp.OR,  False),
        FUNCT_AND_NOT_A: (ALUOp.AND, True),
    }

    _REG_NAMES = [f"t{i}" for i in range(8)]

    def decode(self, instruction: int) -> DecodedInstruction:
        opcode = (instruction >> 26) & 0x3F
        rs = (instruction >> 21) & 0x1F
        rt = (instruction >> 16) & 0x1F
        rd = (instruction >> 11) & 0x1F
        shamt = (instruction >> 6) & 0x1F
        funct =  instruction & 0x3F

        if opcode != OPCODE_RTYPE:
            raise ValueError(f"Unsupported opcode: {opcode:#010b}")

        if funct not in self._FUNCT_TABLE:
            raise ValueError(f"Unknown funct field: {funct:#08b}")

        alu_op, invert_a = self._FUNCT_TABLE[funct]

        rn = self._REG_NAMES
        if alu_op == ALUOp.AND and invert_a:
            mnemonic = f"and {rn[rd]}, ~{rn[rs]}, {rn[rt]}"
        elif alu_op == ALUOp.AND:
            mnemonic = f"and {rn[rd]}, {rn[rs]}, {rn[rt]}"
        else:
            mnemonic = f"or  {rn[rd]}, {rn[rs]}, {rn[rt]}"

        return DecodedInstruction(
            raw=instruction, opcode=opcode,
            rs=rs, rt=rt, rd=rd, shamt=shamt, funct=funct,
            alu_op=alu_op, invert_a=invert_a, mnemonic=mnemonic,
        )


# Instruction assembler helpers
def encode_rtype(rs: int, rt: int, rd: int, funct: int) -> int:
    # Packs an R-type instruction into a 32-bit word.
    return (
        (OPCODE_RTYPE << 26) |
        (rs << 21) |
        (rt << 16) |
        (rd << 11) |
        (0 << 6) |
        funct
    )


def assemble_program() -> list:
    """
    Returns the three-instruction program as a list of 32-bit words.

    Register map: t0=0 t1=1 t2=2 t3=3 t4=4 t5=5 t6=6

    and t4, t0, t1:     t4 = A & B - funct = FUNCT_AND
    and t6, t5, t3:     t6 = (~C) & D - funct = FUNCT_AND_NOT_A  (t5 holds C)
    or  t0, t4, t6:     t0 = t4 | t6 - funct = FUNCT_OR

    t5 is initialised with the value of C (t2) so that t2 is preserved for reference.
    """
    return [
        encode_rtype(rs=0, rt=1, rd=4, funct=FUNCT_AND),    # and t4, t0, t1
        encode_rtype(rs=5, rt=3, rd=6, funct=FUNCT_AND_NOT_A),  # and t6, ~t5, t3
        encode_rtype(rs=4, rt=6, rd=0, funct=FUNCT_OR),     # or  t0, t4, t6
    ]
