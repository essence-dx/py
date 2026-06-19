# Worker Lane 2 Receipt: Simple-Return Backend

Date: 2026-06-01

Lane ID: 2

Worktree: `G:\Dx\python\worktrees\worker-lane-2-simple-return-backend`

Branch: `worker/lane-2-simple-return-backend`

Base commit: `d1967a4f7de Add semantic simple-return IR and stack guards`

## Files Changed

- `Python/native_backend.c`
- `TODO.md` (Lane 2 section only)

## Functionality Added Or Fixed

- Hardened simple-return backend payload installation by validating
  `value_check_index` uop shape, jump target, and exact exit-stub shape before
  the payload can be installed.
- Added runtime simple-return payload-shape checks after magic/version
  validation so stale or malformed fixed-offset payloads fail before helper
  execution.
- Required `expected_ip` and `set_ip` code pointers to be in-bounds and aligned
  to `_Py_CODEUNIT`.
- Added a native simple-return finish guard requiring an empty callee operand
  stack before frame clear/pop.
- Reordered `native_frame_local_slot()` null checks before borrowing the frame
  executable.
- Preserved optimizer/executor formation policy. This does not add natural
  simple-return runtime hits, speedup evidence, or broad native support.

## Subagent Findings Used

- Codebase explorer A found pointer-alignment and payload-shape validation
  gaps in `native_simple_return_code_pointer_valid()` and
  `native_simple_return_data_from_executor()`.
- Codebase explorer B and the test/failure designer found that simple-return
  backend payload projection is still missing compared with range-loop payload
  helpers; recorded as follow-up because it touches `_testinternalcapi` and
  Python tests outside this packet's backend-only ownership.
- Code-quality reviewer identified that `native_fill_simple_return_data()`
  trusted guarded-local value-check uop shape too much; this became the primary
  implemented fix.
- CPython semantic-risk reviewer recommended an empty-stack guard before
  simple-return frame teardown; this was implemented in `native_finish_simple_return()`.
- Integration/conflict reviewer confirmed the TODO Lane 2 title conflict and
  recommended an assignment override plus this receipt.

## Commands Run And Logs

- `git status --short --branch`
- `git worktree add G:\Dx\python\worktrees\worker-lane-2-simple-return-backend -b worker/lane-2-simple-return-backend lane/deoptimization`
- Read-only doc/source inspection with `Get-Content` and `rg`
- `git diff --check`
  - Log: `G:\Dx\python\artifacts\logs\lane2-simple-return-backend-diff-check-20260601.log`
- Source guard for backend hardening hooks
  - Log: `G:\Dx\python\artifacts\logs\lane2-simple-return-backend-source-guard-20260601.log`
- CPU/memory guard from the packet
  - Log: `G:\Dx\python\artifacts\logs\lane2-simple-return-backend-cpu-guard-20260601.log`

## Heavy Commands Deferred

- `PCbuild\build.bat -p x64 -c Debug --experimental-jit`
- Focused native runtime tests
- Broad tests and benchmarks

Reason: packet CPU guard deferred heavy commands twice because CPU was above
the 75% threshold: first `CPU=97.8 FreeGB=7.69 HeavyProcs=0`, then
`CPU=91.6 FreeGB=7.28 HeavyProcs=0`.

## Known Risks

- Source-only verification cannot prove MSVC compile success or native runtime
  behavior.
- Simple-return backend payload projection remains indirect; future helper
  coverage should expose simple-return payload header/shape without claiming
  runtime native hits.
- Targeted `sys.setprofile` regression coverage remains a Lane 7/test follow-up.
- The main checkout is dirty from other lanes, so integration should cherry-pick
  or patch-select this work rather than staging broadly.

## Remaining Work

- Run the guarded Debug JIT build and focused native tests when CPU load allows.
- Add `_testinternalcapi` simple-return payload projection helpers and focused
  tests in the appropriate tooling/test lane.
- Add profile-hook regression evidence for simple-return native-entry deopt.
- Integrator should reconcile the Lane 2 assignment conflict in `TODO.md`.

## Suggested Score Delta

Suggested score delta: `+0.2` overall at most.

Evidence: this is a real backend correctness hardening slice, but it is
source-guarded only and does not prove new emitted-and-executed native runtime
coverage.

## Commit SHA

Not committed.
