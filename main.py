"""
main.py

Entry point for the Single-Cycle 32-bit Processor Simulator.

Computes:  Y = A·B + C'·D

Run:
    - python main.py
    - python main.py --A 1 --B 1 --C 0 --D 1
    - python main.py --all-combinations
"""

import argparse
import sys
from datapath import Datapath
from instruction import assemble_program

RESET = ""
DIM   = ""
SEP   = "─" * 70


def header(text: str) -> str:
    return f"\n{text}{RESET}"


def run_simulation(A: int, B: int, C: int, D: int, verbose: bool = True) -> int:
    # Runs the full processor simulation for a given set of Boolean inputs.

    # Returns the final output Y.
    program = assemble_program()
    dp = Datapath()

    # Pre-loads registers
    dp.load_registers({
        't0': A, 't1': B, 't2': C, 't3': D,
        't5': C,
    })

    traces = dp.run(program)

    if not verbose:
        return traces[-1].registers_after['t0']

    print(SEP)
    print(f"  Single-Cycle Processor Simulation{RESET}")
    print(f"  Target expression : Y = A·B + C'·D")
    print(f"  Input values      : A={A}  B={B}  C={C}  D={D}")
    print(SEP)

    # Initial register snapshot
    print(header("Initial Register State"))
    init = {'t0': A, 't1': B, 't2': C, 't3': D, 't5': C,
            't4': 0, 't6': 0, 't7': 0}
    _print_registers(init)

    # Per-instruction trace
    for i, t in enumerate(traces):
        print(header(f"Instruction {i+1}: {t.mnemonic}"))
        print(f"  Encoding (hex) : {t.instruction_hex}")
        print(f"  Fields         : "
              f"opcode={t.opcode:06b}  "
              f"rs=t{t.rs}  rt=t{t.rt}  rd=t{t.rd}  "
              f"funct={t.funct:06b}")
        cs = t.control_signals
        print(f"  Control signals: "
              f"reg_write={cs['reg_write']}  "
              f"alu_op={cs['alu_op']:<3}  "
              f"invert_a={cs['invert_a']}  "
              f"mux_reg_dst={cs['mux_reg_dst']}")
        if cs['invert_a']:
            print(f"  ALU operands   : "
                  f"A=~{t.operand_a} ({(~t.operand_a) & 0xFFFFFFFF})  "
                  f"B={t.operand_b}")
        else:
            print(f"  ALU operands   : A={t.operand_a}  B={t.operand_b}")
        print(f"  ALU result     : {t.alu_result}{RESET}")
        print(f"  Write-back     : {t.dest_reg_name} <- {t.alu_result}")
        print(f"\n  {DIM}Registers after instruction:{RESET}")
        _print_registers(t.registers_after, highlight=t.dest_reg_name)

    # Summary
    Y = traces[-1].registers_after['t0']
    t4 = traces[0].registers_after['t4']
    t6 = traces[1].registers_after['t6']

    print(f"\n{SEP}")
    print(header("Execution Summary: "))
    print(f"  t4 = A & B    = {A} & {B}     = {t4}{RESET}")
    print(f"  t6 = (~C) & D = ~{C} & {D}    = {t6}{RESET}")
    print(f"  Y  = t4 | t6  = {t4} | {t6}   = {Y}{RESET}")
    print()

    # Verifies against direct computation
    expected = int(bool((A & B) | ((~C & 0x1) & D)))
    status = "PASS" if Y == expected else "FAIL"
    print(f"  Direct check: (A·B) + (C'·D) = {expected} -> {status}")
    print(SEP)
    return Y


def _print_registers(regs: dict, highlight: str = None) -> None:
    pairs = list(regs.items())
    row = []
    for name, val in pairs:
        if name == highlight:
            row.append(f"  {name}={val}{RESET}")
        else:
            row.append(f"  {DIM}{name}={val}{RESET}")
    print("".join(row))


def run_all_combinations() -> None:
    # Runs all 16 Boolean input combinations and display a truth table.
    program = assemble_program()
    print(SEP)
    print(f"  Truth Table — Y = A·B + C'·D{RESET}")
    print(SEP)
    print(f"  {'A':>3} {'B':>3} {'C':>3} {'D':>3} │ {'t4=A&B':>7} {'t6=~C&D':>8} │ {'Y':>3}")
    print(f"  {'─'*3} {'─'*3} {'─'*3}  {'─'*3}  {'─'*7} {'─'*8}  {'─'*3}")

    for A in range(2):
        for B in range(2):
            for C in range(2):
                for D in range(2):
                    dp = Datapath()
                    dp.load_registers({'t0': A, 't1': B, 't2': C,
                                       't3': D, 't5': C})
                    traces = dp.run(program)
                    t4 = traces[0].registers_after['t4']
                    t6 = traces[1].registers_after['t6']
                    Y  = traces[2].registers_after['t0']
                    print(f"  {A:>3} {B:>3} {C:>3} {D:>3} │ {t4:>7} {t6:>8} │ {Y:>3}")
    print(SEP)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Single-Cycle Processor Simulator — Y = A·B + C'·D"
    )
    parser.add_argument("--A", type=int, default=1, choices=[0, 1])
    parser.add_argument("--B", type=int, default=1, choices=[0, 1])
    parser.add_argument("--C", type=int, default=0, choices=[0, 1])
    parser.add_argument("--D", type=int, default=1, choices=[0, 1])
    parser.add_argument(
        "--all-combinations",
        action="store_true",
        help="Run all 16 input combinations and print a truth table",
    )
    args = parser.parse_args()

    if args.all_combinations:
        run_all_combinations()
    else:
        run_simulation(args.A, args.B, args.C, args.D)


if __name__ == "__main__":
    main()
