# Notes for assistant sessions

This repo holds an animation pipeline: Moho 2D characters, Maya or Blender 3D,
voice and lip-sync, assembly, and a YouTube channel. The artwork is human-made;
assistants handle the labor around it.

## Before doing anything

1. Use the `animation-pipeline` skill in `.claude/skills/animation-pipeline/`.
   It has the ground rules, the tools and what has and has not been verified.
2. Read `pipeline/README.md` for the user's standing decisions.
3. Check `pipeline/tickets/` for open work in the lane, and the newest file in
   `pipeline/journal/`.

## While working

- Never overwrite a source `.moho`, scene file or recording. Write a new file.
- Keep "verified" and "expected" apart in everything written down.
- Work one ticket in one lane. Claim it before starting.
- Anything that needs Moho or Maya open belongs to the user's machine. If this
  session cannot do it, write the ticket so a local session or the user can.
- No model names or identifiers in files or commit messages; use `cloud`,
  `local`, `chat` or `human` to say who did something.
- No personal details about the user in the repo.

## Before ending the session

Append a handoff entry to the ticket (done, changed, verified and how, not
verified, next step), add a journal entry if something was learned, commit and
push. Format: `.claude/skills/animation-pipeline/references/collaboration.md`.
