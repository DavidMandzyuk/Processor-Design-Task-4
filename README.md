# Single-Cycle Processor Design
### Processor Design Semester Project - Task4:

Computes: **Y = A·B + C'·D**

---

## Project Structure

```
processor/
├── register_file.py   — 8×32-bit register file (2 read ports, 1 write port)
├── alu.py             — ALU: AND, OR, with optional input-A inversion
├── instruction.py     — 32-bit R-type instruction encoder / decoder
├── control_unit.py    — Control unit: decodes funct field → control signals
├── mux.py             — 2-to-1 MUX and RegDst MUX
├── datapath.py        — Wires all stages: Fetch→Decode→Execute→Write-back
├── main.py            — Simulator entry point + pretty-printed trace
└── README.md
```

---

## Instruction Set

| Instruction | funct (6-bit) | Operation         |
|-------------|---------------|-------------------|
| `and`       | `000001`      | rd = rs & rt      |
| `or`        | `000010`      | rd = rs \| rt     |
| `and` (NOT) | `100001`      | rd = (~rs) & rt   |

**NOT is not a separate instruction.** It is implemented via bit 5 of the
`funct` field (`invert_a` flag), which causes the ALU to bitwise-invert
input A before applying the AND operation.

### 32-bit R-type Encoding

```
 31      26  25    21  20    16  15    11  10     6  5          0
 [ opcode ]  [  rs  ]  [  rt  ]  [  rd  ]  [ shamt ]  [  funct  ]
   000000      5 bits    5 bits    5 bits    00000      6 bits
```

---

## The Program

```asm
# Register map: t0=A, t1=B, t2=C, t3=D  (t5 = copy of C)

and  t4, t0, t1     # t4 = A & B           funct=000001
and  t6, t5, t3     # t6 = (~C) & D        funct=100001  (invert_a=1)
or   t0, t4, t6     # t0 = t4 | t6 = Y     funct=000010
```

---

## Control Signals

| Instruction  | `reg_write` | `alu_op` | `invert_a` | `mux_reg_dst` |
|--------------|-------------|----------|------------|---------------|
| `and t4,...` | 1           | AND      | 0          | 1             |
| `and t6,...` | 1           | AND      | **1**      | 1             |
| `or  t0,...` | 1           | OR       | 0          | 1             |

---

## Running the Simulator

### Default run (A=1, B=1, C=0, D=1)
```bash
python main.py
```

### Custom inputs
```bash
python main.py --A 1 --B 0 --C 1 --D 1
```

### Full truth table (all 16 combinations)
```bash
python main.py --all-combinations
```

---

## Sample Output (A=1, B=1, C=0, D=1)

```
──────────────────────────────────────────────────────────────────────
  Single-Cycle Processor Simulation
  Target expression : Y = A·B + C'·D
  Input values      : A=1  B=1  C=0  D=1
──────────────────────────────────────────────────────────────────────

Initial Register State
  t0=1  t1=1  t2=0  t3=1  t5=0  t4=0  t6=0  t7=0

Instruction 1: and t4, t0, t1
  Encoding (hex) : 0x00012001
  Fields         : opcode=000000  rs=t0  rt=t1  rd=t4  funct=000001
  Control signals: reg_write=1  alu_op=AND  invert_a=0  mux_reg_dst=1
  ALU operands   : A=1  B=1
  ALU result     : 1
  Write-back     : t4 <- 1

  Registers after instruction:
  t0=1  t1=1  t2=0  t3=1  t4=1  t5=0  t6=0  t7=0

Instruction 2: and t6, ~t5, t3
  Encoding (hex) : 0x00A33021
  Fields         : opcode=000000  rs=t5  rt=t3  rd=t6  funct=100001
  Control signals: reg_write=1  alu_op=AND  invert_a=1  mux_reg_dst=1
  ALU operands   : A=~0 (4294967295)  B=1
  ALU result     : 1
  Write-back     : t6 <- 1

  Registers after instruction:
  t0=1  t1=1  t2=0  t3=1  t4=1  t5=0  t6=1  t7=0

Instruction 3: or  t0, t4, t6
  Encoding (hex) : 0x00860002
  Fields         : opcode=000000  rs=t4  rt=t6  rd=t0  funct=000010
  Control signals: reg_write=1  alu_op=OR   invert_a=0  mux_reg_dst=1
  ALU operands   : A=1  B=1
  ALU result     : 1
  Write-back     : t0 <- 1

  Registers after instruction:
  t0=1  t1=1  t2=0  t3=1  t4=1  t5=0  t6=1  t7=0

──────────────────────────────────────────────────────────────────────

Execution Summary: 
  t4 = A & B    = 1 & 1     = 1
  t6 = (~C) & D = ~0 & 1    = 1
  Y  = t4 | t6  = 1 | 1   = 1

  Direct check: (A·B) + (C'·D) = 1 -> PASS
──────────────────────────────────────────────────────────────────────
```

---

## Design Decisions

1. **NOT via funct field** — Bit 5 of the `funct` field acts as an
   `invert_a` flag.  The Control Unit reads this bit and asserts the
   `invert_a` signal to the ALU; no separate NOT opcode is needed.

2. **t5 as a scratch register** — The program uses `t5` (pre-loaded
   with C) as the rs for the second AND instruction, so that t2 (the
   canonical C register) is preserved for inspection.

3. **32-bit masking** — All register reads/writes and ALU results are
   masked to 32 bits (`& 0xFFFFFFFF`).

4. **Modular files** — Each datapath stage lives in its own `.py` file
   matching the requirement for separate programming files per component.
