"""
register_file.py

Register File for the Single-Cycle 32-bit Processor.

Supports:
  - 8 general-purpose 32-bit registers (t0-t7)
  - Two simultaneous read ports
  - One write port
"""


class RegisterFile:
    NUM_REGISTERS = 8
    REGISTER_NAMES = [f"t{i}" for i in range(NUM_REGISTERS)]

    def __init__(self):
        # Initializes all registers to 0.
        self._registers = [0] * self.NUM_REGISTERS

    # Public API
    def read(self, reg_num: int) -> int:
        # Reads a 32-bit value from register *reg_num*.
        self._validate(reg_num)
        return self._registers[reg_num] & 0xFFFFFFFF

    def write(self, reg_num: int, value: int, write_enable: bool = True) -> None:
        # Writes *value* to register *reg_num* when *write_enable* is True.
        if not write_enable:
            return
        self._validate(reg_num)
        self._registers[reg_num] = value & 0xFFFFFFFF

    def load_values(self, values: dict) -> None:
        # Pre-loads registers by name.
        for name, val in values.items():
            idx = self.REGISTER_NAMES.index(name)
            self._registers[idx] = val & 0xFFFFFFFF

    def dump(self) -> dict:
        # Returns a dict of {register_name: value} for all registers.
        return {name: self._registers[i] for i, name in enumerate(self.REGISTER_NAMES)}

    # Internal helpers
    def _validate(self, reg_num: int) -> None:
        if not (0 <= reg_num < self.NUM_REGISTERS):
            raise ValueError(
                f"Register index {reg_num} out of range "
                f"(valid: 0–{self.NUM_REGISTERS - 1})"
            )

    def __repr__(self) -> str:
        entries = ", ".join(
            f"{name}={self._registers[i]}"
            for i, name in enumerate(self.REGISTER_NAMES)
        )
        return f"RegisterFile({entries})"
