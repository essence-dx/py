# Worker Lane 5 Receipt: Range-Loop Runtime

Date: 2026-06-01

## Lane ID And Worktree

- Lane ID: 5
- Lane packet: Range-Loop Runtime
- Worktree: `G:\Dx\python\worktrees\worker-lane-5-range-loop-runtime`
- Branch: `worker/lane-5-range-loop-runtime`
- Base commit: `d1967a4f7de`
- Commit SHA: not committed

## Files Changed

- `Python/native_range_loop_runtime.c`
- `Lib/test/test_tools/test_native_jit_tools.py`

`TODO.md` was not edited because this worktree still contains the older Lane 5
Types/Containers section. Per the worker packet, this receipt records the lane
5 range-loop-runtime work instead.

## Functionality Added/Fixed

- Added `native_range_loop_range_iter_can_advance()` in the range-loop runtime.
- Reused that helper in the direct expression runtime path, replacing the
  duplicated inline `range_iter->start + range_iter->step` overflow guard.
- Added the same guard to `_PyNativeRangeLoop_ExecuteIntAccum()` after
  exhaustion handling and before `range_iter->start = value + range_iter->step`.
- Added a source-boundary test proving the plain int-accum runtime checks
  zero-step and signed-`long` advance overflow before mutating the range
  iterator, and deopts through `data->iter_check_exit_target`.

This is a correctness hardening change only. It does not claim broader native
support or speedup.

## Commands Run And Log Paths

- RED evidence:
  - Inline source check failed before implementation with:
    `AssertionError: missing shared range iterator advance guard`
- Lightweight verification:
  - `python -m py_compile Lib\test\test_tools\test_native_jit_tools.py`
    - Log: `G:\Dx\python\artifacts\logs\pycompile-lane5-range-loop-runtime-20260601.log`
  - Inline source check for the new guard and ordering
    - Log: `G:\Dx\python\artifacts\logs\source-check-lane5-range-loop-advance-guard-20260601.log`
  - `git diff --check -- Python/native_range_loop_runtime.c Lib/test/test_tools/test_native_jit_tools.py`
    - Log: `G:\Dx\python\artifacts\logs\diff-check-lane5-range-loop-runtime-20260601.log`
- Heavy gates:
  - Initial gate deferred heavy commands: CPU was 100 percent.
  - Later gate passed: CPU 41.8 percent, FreeGB 7.78, HeavyProcs 0.
    - Log: `G:\Dx\python\artifacts\logs\heavy-gate-lane5-range-loop-runtime-20260601.log`
  - Pre-test gate passed: CPU 35.6 percent, FreeGB 7.95, HeavyProcs 0.
    - Log: `G:\Dx\python\artifacts\logs\heavy-gate-lane5-range-loop-runtime-before-test-20260601.log`
- Build:
  - `.\PCbuild\build.bat -p x64 -c Debug --experimental-jit`
    - Result: passed, 0 warnings, 0 errors
    - Log: `G:\Dx\python\artifacts\logs\pcbuild-debug-x64-jit-lane5-range-loop-runtime-20260601.log`
- Focused tests:
  - `.\python.bat -m test -j6 test_tools -m test_range_loop_int_accum_guards_range_iterator_advance_overflow -v`
    - Result: passed, 1 filtered test
    - Log: `G:\Dx\python\artifacts\logs\regrtest-lane5-range-loop-source-boundary-20260601.log`
  - `.\python.bat -m test -j6 test_capi -m test_range_loop_direct_path_handles_wide_int_boundaries -v`
    - Result: command passed, 1 filtered test selected, test skipped because
      Debug native range-loop backend emission was unavailable
    - Log: `G:\Dx\python\artifacts\logs\regrtest-lane5-range-loop-wide-boundaries-20260601.log`

## Heavy Commands Deferred Due CPU/Memory

- Heavy commands were initially deferred because the first gate reported
  `CPU=100 FreeGB=8.49 HeavyProcs=0`.
- After CPU dropped below the threshold, the build and focused tests were run.

## Known Risks

- The focused runtime `test_capi` command did not provide native-hit proof. It
  skipped because Debug range-loop backend emission was unavailable
  (`range_loop_backend_emitted == 0`).
- The change is source/build verified and covered by a source-boundary test,
  but not proven by an emitted-and-executed native helper path on this machine.
- The branch still needs deeper range-loop runtime hardening for:
  - direct-advance preflight range-iterator uniqueness under `Py_GIL_DISABLED`;
  - upper-bound/alignment validation before reading `stack_pointer[-2]`;
  - checked arithmetic in `native_range_loop_rollback_direct_range_iter()`;
  - avoiding future drift between direct expression and plain int-accum pending
    and resume handling.
- Build artifacts and generated `python.bat` now exist in the worktree as a
  result of the successful Debug build.

## Remaining Work

- Add a lane-owned test and fix for direct-advance preflight uniqueness before
  emitted native direct advance can mutate shared range iterators in
  free-threaded builds.
- Harden direct rollback arithmetic so large `iteration_count * step` cannot
  overflow before the rollback guard reports failure.
- Add stack-pointer upper-bound/alignment validation to the direct-prepare path
  or route that preflight through the same publication/validation discipline as
  normal runtime entry.
- Rerun focused runtime tests on a configuration where native range-loop backend
  emission is available, then require emitted-and-executed diagnostics before
  claiming native execution proof.

## Suggested Score Delta With Evidence

- Overall project: `34/100` -> `34.2/100`.
- Focused range-loop acceleration lane: `62/100` -> `62.5/100`.

Evidence: the patch removes one release-mode signed-overflow risk in an existing
range-loop runtime path, builds cleanly, and adds a focused source-boundary
regression. It does not improve native hit rate or broaden supported Python
semantics.

## Subagent Summary

- Six GPT-5.5 xhigh subagents were spawned.
- Five returned before the first collection pass; the sixth returned before
  final receipt writing.
- Multiple subagents independently identified the unchecked plain int-accum
  range iterator advance as the highest-risk small lane-owned fix.
- Other subagent findings were recorded as remaining work rather than folded
  into this checkpoint.
