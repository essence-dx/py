# Worker Lane 4 Receipt - Deopt And Stack Safety

Date: 2026-06-01

Lane ID: 4

Worktree: `G:\Dx\python\worktrees\worker-lane-4-deopt-stack-safety`

Branch: `worker/lane-4-deopt-stack-safety`

Base: `d1967a4f7de Add semantic simple-return IR and stack guards`

## Scope Note

The assignment packet names Lane 4 as Deopt And Stack Safety. The branch
`TODO.md` still labels Lane 4 as Object Model And Numeric Semantics. I kept the
source work inside the packet's deopt/stack-safety scope and appended a new
receipt subsection inside the existing Lane 4 TODO section instead of rewriting
lane headings or relocating older notes.

## Files Changed

- `Python/native_backend.c`
- `Lib/test/test_tools/test_native_jit_tools.py`
- `TODO.md`
- `G:\Dx\python\artifacts\receipts\worker-lane-4-deopt-stack-safety.md`

## Functionality Added

- Added executor/frame-code mismatch guards to specialized direct
  simple-return helper paths before payload lookup or native entry-state
  mutation.
- Reordered `native_apply_simple_return_prefix()` so invalid simple-return
  executors clear any side-exit state through
  `native_clear_exit_with_stack_pointer()` before instrumentation/eval-breaker
  deopt can win.
- Covered these helper paths:
  `native_immortal_const_return_entry()`,
  `native_immortal_const_result_return()`,
  `native_fast_local_result_return()`,
  `native_fast_local_clear_result_return()`,
  `native_none_local_result_return()`, and
  `native_bool_local_source_return()`.
- Extended the source-boundary test
  `test_simple_return_entries_guard_code_before_payload_or_entry_state()` so it
  checks generic simple-return entry, guarded-source entry, and specialized
  direct helpers.
- The test now requires the code-frame guard to run before
  `native_simple_return_data_from_executor()` and
  `native_enter_executor()`, and verifies the mismatch branch uses
  `native_error_return()` with a mismatched executor-code message.
- Added source-boundary coverage proving invalid-executor cleanup in
  `native_apply_simple_return_prefix()` stays after the frame/code guard,
  before instrumentation fallback, and uses the release-safe side-exit cleanup
  helper.

## Commands Run

- Red source guard:
  `G:\Dx\python\artifacts\logs\red-lane4-simple-return-entry-code-guard-20260601.log`
  - Failed as expected before implementation with
    `immortal_const_return missing executor/frame code guard`.
- Green source guard:
  `G:\Dx\python\artifacts\logs\green-lane4-simple-return-entry-code-guard-20260601.log`
  - Passed.
- Red invalid-executor ordering guard:
  `G:\Dx\python\artifacts\logs\red-lane4-simple-return-invalid-executor-side-exit-20260601.log`
  - Failed as expected before implementation with
    `invalid executor side-exit cleanup must run before instrumentation deopt`.
- Green invalid-executor ordering guard:
  `G:\Dx\python\artifacts\logs\green-lane4-simple-return-invalid-executor-side-exit-20260601.log`
  - Passed.
- Syntax check:
  `python -m py_compile Lib\test\test_tools\test_native_jit_tools.py`
  - Log:
    `G:\Dx\python\artifacts\logs\pycompile-lane4-simple-return-entry-code-guard-20260601.log`
  - Exit 0.
- Diff whitespace check:
  `git diff --check -- Python/native_backend.c Lib/test/test_tools/test_native_jit_tools.py`
  - Log:
    `G:\Dx\python\artifacts\logs\diff-check-lane4-simple-return-entry-code-guard-20260601.log`
  - Exit 0 with LF-to-CRLF warnings only.
- Final diff whitespace check including TODO:
  `git diff --check -- Python/native_backend.c Lib/test/test_tools/test_native_jit_tools.py TODO.md`
  - Log:
    `G:\Dx\python\artifacts\logs\diff-check-lane4-simple-return-entry-code-guard-final-20260601.log`
  - Exit 0 with LF-to-CRLF warnings only.
- Built interpreter probe:
  `Test-Path .\PCbuild\amd64\python.exe`
  - Result: `False`.

## Heavy Commands

- No heavy build, broad test, runtime native probe, or benchmark was attempted.
- The packet's CPU/memory gate was not run because no heavy command was
  attempted.

## Known Risks

- This is source-boundary evidence, not runtime native execution proof.
- The isolated worktree lacks `PCbuild\amd64\python.exe`, so focused runtime
  native tests could not run.
- The broader repo has active lane overlap around `Python/native_backend.c` and
  `Lib/test/test_tools/test_native_jit_tools.py`; integration should reconcile
  with other workers before merging.
- The existing TODO Lane 4 title conflicts with the current packet's Lane 4
  deopt/stack-safety assignment.

## Remaining Work

- Add release-safe two-slot stack-capacity validation before range-loop operand
  deopt paths write `stack_pointer[0]` and `stack_pointer[1]`.
- Consider making `native_unpublish_stack_pointer_if_needed()` behavior
  identical in release and debug builds.
- Centralize range-loop runtime raw error-target pointer arithmetic behind
  validated target helpers.
- Consider instruction-target alignment validation for deopt/`SET_IP` targets,
  not just in-code-object bounds checks.
- Run a focused rebuilt native runtime check once a built interpreter is
  available.

## Subagents

- Six read-only subagents were spawned as requested.
- Completed before this receipt: codebase explorer, second codebase explorer,
  test/failure designer, code-quality reviewer, CPython semantic-risk reviewer,
  and integration/conflict reviewer.

## Suggested Score Delta

Suggested delta: +0.2 overall project points at most.

Evidence: the patch improves one release-safety guard family for direct
simple-return helper fallback paths, with red/green source-boundary evidence.
It does not prove runtime native hits, broad deopt correctness, benchmarks, or
CPython-wide compatibility.

## Commit

Not committed.
