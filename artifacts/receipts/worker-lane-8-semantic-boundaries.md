# Worker Lane 8 Receipt: Semantic Boundaries

## Lane ID And Worktree

- Lane ID: 8
- Worktree: `G:\Dx\python\worktrees\worker-lane-8-semantic-boundaries`
- Branch: `worker/lane-8-semantic-boundaries`
- Base: `lane/deoptimization` at `d1967a4f7de Add semantic simple-return IR and stack guards`

## Files Changed

- `Include/internal/pycore_native_plan.h`
- `Include/internal/pycore_native_uop.h`
- `Python/native_plan.c`
- `Python/native_semantic_boundary.c`
- `Python/native_eligibility.c`
- `Python/native_ir.c`
- `Python/native_simple_return.c`
- `Python/native_backend.c`
- `Modules/_testinternalcapi/native_jit.c`
- `Lib/test/test_capi/test_native_jit.py`
- `Lib/test/test_tools/test_native_jit_tools.py`

`TODO.md` was not edited because its Lane 8 section currently describes
profiling/reference/GC/thread work, while this packet assigns Lane 8 to
semantic boundaries. This receipt records the work instead of mutating the
wrong lane ledger section.

## Functionality Added Or Fixed

- Added diagnostic-only native trace kinds for generator and exception semantic
  boundaries.
- Added public test names `generator_boundary` and `exception_boundary`.
- Extended semantic-boundary classification to include generator, coroutine /
  await, exception, with/finally/setup, and frame-entry call boundary signals.
- Moved semantic-boundary scanning before loop and simple-return planning so
  dangerous Python-visible uops cannot be shadowed by later planner branches.
- Kept semantic-boundary plans non-emittable and ineligible:
  `backend_emittable=false`, `eligible=false`, `decline_not_emittable`.
- Added `_testinternalcapi` synthetic helper shapes for `generator` and
  `exception`.
- Extended focused tests so generator and exception boundaries are covered by
  source-boundary checks and semantic-boundary plan assertions.

## Commands Run

- RED source-boundary harness for
  `NativeSourceBoundaryTests.test_semantic_boundary_planner_covers_generator_and_exception_edges`
  before implementation: failed as expected.
- GREEN source-boundary harness for the same test after implementation:
  passed.
- `python -m py_compile Lib\test\test_tools\test_native_jit_tools.py Lib\test\test_capi\test_native_jit.py`: passed.
- `git diff --check -- Include/internal/pycore_native_plan.h Include/internal/pycore_native_uop.h Lib/test/test_capi/test_native_jit.py Lib/test/test_tools/test_native_jit_tools.py Modules/_testinternalcapi/native_jit.c Python/native_backend.c Python/native_eligibility.c Python/native_ir.c Python/native_plan.c Python/native_semantic_boundary.c Python/native_simple_return.c`: passed with only LF-to-CRLF warnings.

No separate log files were created; commands were lightweight and run inline.

## Heavy Commands

- No CPython build, native runtime test, broad test suite, or benchmark was run.
- Heavy commands were not attempted, so no CPU/memory defer check was needed.

## Known Risks

- `TODO.md` lane numbering conflicts with the packet. The repository ledger says
  Lane 8 is profiling/reference/GC/thread work, while this packet says Lane 8 is
  semantic boundaries.
- Runtime `_testinternalcapi` semantic-boundary plan tests were updated but not
  executed on a rebuilt CPython binary.
- Full `NativeSourceBoundaryTests` was tried once and still has an unrelated
  simple-return frame-cleanup source assertion failure. The new Lane 8 semantic
  boundary source test passes in isolation.
- The semantic-boundary classifier is still a large switch. Future work should
  consider a centralized metadata/predicate table to reduce missed-switch drift.
- Diagnostic-only semantic boundaries still use the existing generic
  `decline_not_emittable` reason instead of a new explicit semantic-boundary
  eligibility reason.

## Remaining Work

- Integrator should reconcile `TODO.md` Lane 8 ownership with this packet or
  move this work under the existing semantic-boundary lane entry.
- Run rebuilt CPython focused tests for
  `NativeSemanticBoundaryPlanTests.test_lane2_semantic_boundaries_are_diagnostic_only`
  after the next build is available.
- Consider explicit semantic-boundary eligibility reasons and stats fields in a
  coordinated diagnostics pass.
- Add behavior-level synthetic tests for more individual boundary opcodes if
  `_testinternalcapi` is extended to parameterize the boundary opcode directly.

## Suggested Score Delta

- Suggested project score delta: +1 point at most, from 34/100 to 35/100.
- Evidence: generator and exception semantic-boundary planning is now explicit
  and diagnostic-only, and semantic-boundary scanning runs before loop/simple
  planners. No runtime native execution or broad compatibility proof was added.

## Commit SHA

- Not committed.
