# Native CPython Acceleration Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a production-quality CPython fork that can safely accelerate selected Python loops through the existing CPython optimizer and JIT pipeline without breaking normal Python semantics.

**Architecture:** Keep CPython as the source of truth for parsing, bytecode semantics, object behavior, and fallback execution. Add native acceleration only as guarded, diagnosable fast paths for proven hot-loop shapes, and deopt immediately to normal CPython when a guard, overflow check, signal check, or semantic precondition fails.

**Tech Stack:** CPython C internals, tier-2 optimizer traces, CPython JIT/native executor integration, Windows `PCbuild`, CPython regression tests, `_testinternalcapi` diagnostics, and benchmark scripts stored under `G:\Dx\python\artifacts\logs`.

---

## Brutal Status

For the full dream of "make Python generate native machine code and be broadly faster than latest CPython while still supporting current Python," this fork is about **8 out of 100**.

That is not an insult to the work. It means the hard thing is accurately named. The repo already has a real CPython fork, a real native-JIT skeleton, real diagnostics, real Windows builds, and a measured narrow loop win around `total += i % 7`. But it is still a narrow experimental accelerator, not a general Python binary compiler, not a complete AOT compiler, and not production-safe for broad Python code.

For the smaller milestone "native range-loop integer expression acceleration with safe fallback," the fork is about **35 out of 100**. At the reset point for this plan, the tree contained an unfinished subtract-expression experiment that could not be committed until it was either proven and green or backed out into a later slice.

## What Has Been Tried

- Created and configured the CPython fork under `G:\Dx\python\cpython` with `origin` pointing to `millercarla211-ctrl/cpython` and `upstream` pointing to `python/cpython`.
- Built the local CPython fork on Windows and confirmed the machine can build it, though builds are expensive on this OS.
- Added a native range-loop acceleration path around CPython optimizer/JIT internals.
- Added internal native acceleration headers and C modules for ABI data, eligibility, planning, emission, fast paths, offsets, and backend execution.
- Added `_testinternalcapi` diagnostics so test code can inspect native-JIT plans, backend compile counts, unsupported helper counts, native iterations, closed-form batches, and backend errors.
- Added stats plumbing through `pystats` and `Tools/scripts/summarize_stats.py`.
- Verified a narrow closed-form expression path for `total += i % 7`, including negative starts.
- Measured a narrow microbenchmark speedup of roughly 42x for `total += i % 7` on this prototype, compared with the same local interpreter with native acceleration disabled.
- Started a new accumulator-subtract slice for expressions such as `total -= i % 7`, `total -= (i % 12) + (i % 8)`, and `total -= (i % 12) - (i % 8)`.
- Observed red tests showing the subtract slice was not green at the reset point: plans existed, but the then-built backend emitted too few subtract-expression helpers.
- After the reset, rebuilt with `--experimental-jit-off` and verified the subtract slice green on the release-with-assert JIT build.

## Non-Negotiable Engineering Rules

- Commit only verified green slices. Do not commit red tests, speculative backend support, or unproven semantic assumptions.
- Keep normal CPython behavior as the fallback for every unsupported or risky case.
- Treat every native fast path as an optimization, never as a new language behavior.
- Every new supported shape needs a RED test first, a GREEN implementation, diagnostics evidence, and a benchmark only after correctness is proven.
- Store command output and benchmark logs under `G:\Dx\python\artifacts\logs`; do not scatter verification output elsewhere.
- On this low-memory Windows machine, batch source edits first, then run one targeted build/test pass instead of rebuilding after every tiny edit.
- Clean `PCbuild\obj` after verified batches when space matters, but keep source files and the built interpreter unless a rebuild is intentionally required.
- Use professional names that describe the real feature, not throwaway names such as `v1`, `magic`, `fast thing`, or `ai`.

## File Responsibilities

- `Include/internal/pycore_native_abi.h`: native backend ABI structures shared by planner, emitter, and executor.
- `Include/internal/pycore_native_backend.h`: backend diagnostics and native backend entry points.
- `Include/internal/pycore_native_eligibility.h`: trace-shape eligibility contracts.
- `Include/internal/pycore_native_emit.h`: machine-code/native stub emission contracts.
- `Include/internal/pycore_native_fastpath.h`: opcode and trace fast-path helpers.
- `Include/internal/pycore_native_offsets.h`: generated or maintained offsets needed by native code.
- `Include/internal/pycore_native_plan.h`: native loop plan structures and enum definitions.
- `Python/native_eligibility.c`: maps CPython uops into native-supported operation kinds.
- `Python/native_plan.c`: recognizes safe range-loop shapes and records exact expression plans.
- `Python/native_backend.c`: executes guarded native range-loop helpers and closed-form batches.
- `Python/native_emit.c`: emits native stubs or connects backend helpers to the executor.
- `Python/native_fastpath.c`: filters opcode sequences and fast-path eligibility.
- `Python/jit.c`, `Python/optimizer.c`, `Python/optimizer_analysis.c`: integration points with CPython's JIT and optimizer.
- `Modules/_testinternalcapi.c`: test-only inspection and diagnostics API.
- `Lib/test/test_capi/test_native_jit.py`: regression tests for native-JIT planning, fallback, diagnostics, and semantics.
- `Tools/scripts/summarize_stats.py`: human-readable summaries for native-JIT stats.
- `PCbuild/*.vcxproj`: Windows build wiring for new C files and generated support.

## Current Risk Register

- **Resolved for this slice:** The accumulator-subtract expression tests are green on the release-with-assert JIT build.
- **Resolved for this slice:** `_Py_NATIVE_RANGE_LOOP_INT_OP_SUBTRACT_INPLACE_RIGHT` was proven from CPython source to compute `left - right` while mutating the right operand, and the subtract-expression test now asserts the runtime plan exercises this operation kind.
- **Critical:** Negative range starts must never trigger signed overflow in native closed-form count clamping.
- **Critical:** Native fast paths must deopt without advancing iterators or corrupting locals when arithmetic overflows into Python big integers.
- **Important:** Runtime diagnostics must show both compile-time plan emission and execution-time closed-form/native iteration counts.
- **Important:** Loop variable materialization must preserve Python-visible `i` after batched native iterations.
- **Important:** Non-unit range steps, negative steps, unsupported modulo periods, and pending checks must remain safe fallbacks until explicitly supported.

## Task 1: Freeze The Current Commit Boundary

**Files:**
- Inspect: `G:\Dx\python\cpython\Lib\test\test_capi\test_native_jit.py`
- Inspect: `G:\Dx\python\cpython\Python\native_backend.c`
- Inspect: `G:\Dx\python\cpython\Python\native_plan.c`
- Inspect: `G:\Dx\python\cpython\Python\native_eligibility.c`

- [ ] **Step 1: Capture current tree state**

Run:

```powershell
git -C G:\Dx\python\cpython status --short --branch
git -C G:\Dx\python\cpython diff --stat
```

Expected: dirty tree on `dev`, with native-JIT source files and `Lib/test/test_capi/test_native_jit.py` present.

- [ ] **Step 2: Decide the commit boundary**

The first professional commit may include:

```text
native range-loop infrastructure
diagnostics
single modulo expression closed form
negative-start safety fix
tests that pass on the local CPython build
```

It must not include:

```text
red accumulator-subtract tests
unproven right-inplace subtract support
benchmarks without correctness tests
large unrelated upstream churn
build artifacts
```

- [ ] **Step 3: Remove or finish unfinished subtract code before staging**

If the subtract slice is still red, remove the unverified test and backend changes from the commit boundary. If it is green, include it only with fresh verification logs.

- [ ] **Step 4: Run whitespace verification**

Run:

```powershell
git -C G:\Dx\python\cpython diff --check *> G:\Dx\python\artifacts\logs\diff-check-native-cpython-acceleration-20260530.log
```

Expected: exit code 0, except pre-existing line-ending warnings are acceptable if Git reports no whitespace errors.

## Task 2: Prove Or Reject Accumulator Subtract Expressions

**Files:**
- Modify: `G:\Dx\python\cpython\Lib\test\test_capi\test_native_jit.py`
- Modify: `G:\Dx\python\cpython\Python\native_backend.c`
- Inspect: `G:\Dx\python\cpython\Python\bytecodes.c`
- Inspect: `G:\Dx\python\cpython\Python\executor_cases.c.h`
- Inspect: `G:\Dx\python\cpython\Python\optimizer_cases.c.h`

- [ ] **Step 1: Keep the supported semantic surface narrow**

Supported for this task:

```text
total -= i % positive_small_int
total -= (i % positive_small_int) + (i % positive_small_int)
total -= (i % positive_small_int) - (i % positive_small_int)
```

Unsupported unless separately proven:

```text
_Py_NATIVE_RANGE_LOOP_INT_OP_SUBTRACT_INPLACE_RIGHT
range step other than 1
modulo by non-positive values
large periods that exceed helper limits
arithmetic that leaves Py_ssize_t
```

- [ ] **Step 2: Write the failing test**

Add or keep a test with this behavioral matrix:

```python
def sub_single(n):
    total = 0
    for i in range(n):
        total -= i % 7
    return total

def sub_sum(n):
    total = 0
    for i in range(n):
        total -= (i % 12) + (i % 8)
    return total

def sub_delta(n):
    total = 0
    for i in range(n):
        total -= (i % 12) - (i % 8)
    return total
```

Use counts:

```python
counts = [0, 1, 7, 8, 12, 13, 64]
```

Assert:

```python
self.assertEqual(payload["results"], payload["expected"])
self.assertGreaterEqual(payload["compile_diagnostics"]["range_loop_backend_emit_attempts"], 3)
self.assertGreaterEqual(payload["compile_diagnostics"]["range_loop_backend_emitted"], 3)
self.assertEqual(payload["compile_diagnostics"]["range_loop_backend_helper_unsupported"], 0)
self.assertEqual(payload["compile_diagnostics"]["range_loop_backend_errors"], 0)
self.assertGreater(payload["diagnostics"]["range_loop_expr_closed_form_batches"], 0)
self.assertEqual(
    payload["diagnostics"]["range_loop_expr_closed_form_iterations"],
    payload["native_iterations"],
)
```

- [ ] **Step 3: Verify RED**

Run:

```powershell
$env:PYTHON_JIT='1'
$env:PYTHON_NATIVE_JIT='1'
$env:PYTHON_NATIVE_JIT_DIAGNOSTICS='1'
G:\Dx\python\cpython\PCbuild\amd64\python.exe -m test test_capi.test_native_jit -m test_range_loop_mod_closed_form_accumulator_subtract -v *> G:\Dx\python\artifacts\logs\test-accumulator-subtract-red-20260530.log
```

Expected: fail because backend emission is incomplete for the subtract expression shapes.

- [ ] **Step 4: Implement only proven subtract kinds**

`native_range_loop_apply_expr_delta()` may map these to `accumulator - delta`:

```c
case _Py_NATIVE_RANGE_LOOP_INT_OP_SUBTRACT:
case _Py_NATIVE_RANGE_LOOP_INT_OP_SUBTRACT_INPLACE:
    return native_checked_sub_ssize(accumulator, delta, out);
```

Do not include `_Py_NATIVE_RANGE_LOOP_INT_OP_SUBTRACT_INPLACE_RIGHT` in this branch unless a source-level and runtime test proves it means the same accumulator update.

- [ ] **Step 5: Prevent negative-start clamp overflow**

Use a guard that avoids subtracting a negative `range_iter->start` from `LONG_MAX`:

```c
if (range_iter->start >= 0) {
    Py_ssize_t max_count =
        (Py_ssize_t)LONG_MAX - (Py_ssize_t)range_iter->start;
    if (count > max_count) {
        count = max_count;
    }
}
```

- [ ] **Step 6: Verify GREEN**

Run:

```powershell
$env:PYTHON_JIT='1'
$env:PYTHON_NATIVE_JIT='1'
$env:PYTHON_NATIVE_JIT_DIAGNOSTICS='1'
G:\Dx\python\cpython\PCbuild\amd64\python.exe -m test test_capi.test_native_jit -m test_range_loop_mod_closed_form_accumulator_subtract -v *> G:\Dx\python\artifacts\logs\test-accumulator-subtract-green-20260530.log
```

Expected: pass with backend emitted count at least 3, helper unsupported count 0, backend errors 0, and closed-form iterations equal native iterations.

## Task 3: Lock Down Fallback And Materialization Semantics

**Files:**
- Modify: `G:\Dx\python\cpython\Lib\test\test_capi\test_native_jit.py`
- Modify: `G:\Dx\python\cpython\Python\native_backend.c` only if tests expose a real bug

- [ ] **Step 1: Add loop-variable materialization coverage**

Use:

```python
def sub_single_with_last(n):
    total = 0
    for i in range(n):
        total -= i % 7
    return total, i
```

Assert:

```python
self.assertEqual(
    payload["results"],
    {str(n): (-sum(i % 7 for i in range(n)), n - 1) for n in [1, 6, 7, 8, 64]},
)
```

- [ ] **Step 2: Add non-unit-step fallback coverage**

Use:

```python
def stepped(n):
    total = 0
    for i in range(0, n, 2):
        total -= i % 7
    return total
```

Assert the result matches Python and that closed-form batch counters do not increase for this function.

- [ ] **Step 3: Add overflow fallback coverage**

Use a seed near `sys.maxsize`:

```python
def overflows_to_bigint(n):
    total = -sys.maxsize
    for i in range(n):
        total -= i % 7
    return total
```

Assert the result matches Python and no iterator/local corruption occurs.

- [ ] **Step 4: Run the targeted fallback test group**

Run:

```powershell
$env:PYTHON_JIT='1'
$env:PYTHON_NATIVE_JIT='1'
$env:PYTHON_NATIVE_JIT_DIAGNOSTICS='1'
G:\Dx\python\cpython\PCbuild\amd64\python.exe -m test test_capi.test_native_jit -m "test_range_loop_*subtract* or test_range_loop_*fallback*" -v *> G:\Dx\python\artifacts\logs\test-native-jit-subtract-fallbacks-20260530.log
```

Expected: all selected tests pass.

## Task 4: Run One Full Native-JIT Verification Batch

**Files:**
- Test: `G:\Dx\python\cpython\Lib\test\test_capi\test_native_jit.py`

- [ ] **Step 1: Build once after source edits settle**

Run:

```powershell
G:\Dx\python\cpython\PCbuild\build.bat -p x64 -c Debug *> G:\Dx\python\artifacts\logs\build-native-cpython-acceleration-20260530.log
```

Expected: exit code 0.

- [ ] **Step 2: Run the full native-JIT test file**

Run:

```powershell
$env:PYTHON_JIT='1'
$env:PYTHON_NATIVE_JIT='1'
$env:PYTHON_NATIVE_JIT_DIAGNOSTICS='1'
G:\Dx\python\cpython\PCbuild\amd64\python.exe -m test test_capi.test_native_jit -v *> G:\Dx\python\artifacts\logs\test-native-jit-full-20260530.log
```

Expected: all tests in `test_native_jit.py` pass.

- [ ] **Step 3: Run the benchmark only after tests pass**

Run the existing benchmark script or inline benchmark used for `total += i % 7`, and store output at:

```text
G:\Dx\python\artifacts\logs\microbench-native-cpython-acceleration-20260530.log
```

Expected: correctness results match Python first; speedup is useful evidence only after correctness passes.

## Task 5: Commit A Professional Slice

**Files:**
- Stage only source, tests, and project files required for the verified slice. Keep workflow plan documents out of the CPython source commit unless the fork intentionally adopts them as project documentation.
- Do not stage: `PCbuild\obj`, binaries, generated logs, `.pyc`, temp probes, or benchmark scratch files.

- [ ] **Step 1: Review staged changes**

Run:

```powershell
git -C G:\Dx\python\cpython status --short
git -C G:\Dx\python\cpython diff --cached --stat
git -C G:\Dx\python\cpython diff --cached --check
```

Expected: staged files match the verified slice and `diff --cached --check` exits 0.

- [ ] **Step 2: Commit**

Use a professional commit message:

```powershell
git -C G:\Dx\python\cpython commit -m "Add native range-loop expression acceleration"
```

Expected: commit succeeds on branch `dev`.

- [ ] **Step 3: Record final state**

Run:

```powershell
git -C G:\Dx\python\cpython status --short --branch *> G:\Dx\python\artifacts\logs\git-status-after-native-cpython-acceleration-20260530.log
git -C G:\Dx\python\cpython log --oneline -1 *> G:\Dx\python\artifacts\logs\git-head-after-native-cpython-acceleration-20260530.log
```

Expected: branch `dev` is ahead by one commit, with no unintended build artifacts staged.

## Task 6: Next Professional Milestones

- [ ] **Milestone A: Affine expression closed forms**

Add support for:

```python
total += i + c
total -= i + c
```

with checked closed-form arithmetic.

- [ ] **Milestone B: General affine integer expressions**

Add support for:

```python
total += a * i + b
total -= a * i + b
```

only after multiplication expression planning and fallback behavior are tested.

- [ ] **Milestone C: Wider Python semantics**

Do not start non-range loops, function calls, containers, exceptions, generators, object attributes, or arbitrary Python bytecode until range-loop semantics are boringly correct.

- [ ] **Milestone D: Binary/AOT research path**

Keep this separate from the native-JIT helper path. AOT binary generation is a different product surface with packaging, imports, extension modules, ABI compatibility, debugging, and deployment concerns.

## Self-Review

- Spec coverage: The plan covers the user's real goal, current work attempted, reset-state risks, next code steps, verification, cleanup, and commit hygiene.
- Placeholder scan: No `TBD`, `TODO`, or vague "handle edge cases" placeholders remain; each task names files, commands, and expected outcomes.
- Type/signature consistency: Native operation names match the existing `_Py_NATIVE_RANGE_LOOP_INT_OP_*` names used in this fork.
- Brutal truth: The whole project is early. The next professional move is a verified native range-loop slice, not a claim that CPython is now broadly compiled to native binaries.
