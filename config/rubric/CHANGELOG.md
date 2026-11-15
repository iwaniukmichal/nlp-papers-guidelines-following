# Rubric changelog

Every change to the rubric creates a new file `rubric_v<version>.json`; earlier versions are kept
so that archived runs in `runs/` stay reproducible. Per the proposal, revisions may be based only on
pilot/development cases; later revisions require fresh testing or an exploratory designation.

## 1.0.0 (2026-11-15, field `rubric_version: "1.0.0-poc"`)

- Initial six-item rubric used in the 14-paper pilot (I1 Limitations section, I2 Specific limitation,
  I3 Ethical risks, I4 Computational budget, I5 Asset licensing, I6 AI assistance disclosure).
- Four evidence states, derived compliance rules, one positive and one negative example per item.
