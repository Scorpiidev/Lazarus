# Working with other instances

Several assistant sessions work on this project: chat conversations, cloud
sessions with a repo checkout, and local sessions on the user's machine. They
do not share memory and usually are not running at the same time. The repo is
what they share.

## The one rule

**If it is not in the repo, the next instance does not know it.** Decisions,
findings, half-finished work and open questions all go into a file before the
session ends. A summary left in a chat window is lost.

## Lanes

A lane is a kind of work with a defined output. An instance takes a lane for a
ticket; it is not a permanent identity.

| Lane | Does | Output contract | Usually runs |
|---|---|---|---|
| story | Topic choice, script, shot list | `script.md`; `lines.json` per shot | Chat, with the user |
| voice | Audio and timing | wavs, `sequence.wav`, `.dat`, `timing.json` | Cloud |
| rig | Builds and documents rigs | `rig.moho`, `rig.json`, `semantics.json`, calisthenics sheet | Local for building, cloud for manifests |
| anim | Scores and revisions | `score.json`, `anim.moho`, `review.md` | Cloud writes, local renders |
| look | Occasional 3D assets and their shaders | PNG renders with alpha, shader source | Local |
| post | Assembly, subtitles, encode | Final video | Cloud |
| insight | Trends and channel analytics | Dated report with evidence | Cloud or chat |

One instance, one ticket, one lane at a time. Crossing lanes mid-ticket is how
two sessions end up editing the same file.

The user owns every decision a viewer would notice: story, design, casting,
what ships. Assistants recommend and then wait on those.

## Tickets

One file per work item in `pipeline/tickets/`, named
`T-<number>-<short-slug>.md`. Separate files mean two sessions rarely touch
the same lines, so pushes do not collide.

```markdown
---
id: T-0007
title: Lip-sync pass for shot 010
lane: voice
status: open        # open | claimed | blocked | review | done
owner:              # cloud | local | chat | human, empty while open
needs: cloud        # cloud | local-moho | local-maya | human | any
inputs: [shows/demo/episodes/01/shots/010/lines.json]
outputs: [shows/demo/episodes/01/shots/010/audio/]
---

## Goal
One or two sentences.

## Done when
A checkable condition, not "works".

## Log
- 2026-11-12 cloud: created.
```

**Claiming.** Set `status: claimed` and `owner`, commit, push. If the push is
rejected because someone else claimed it first, take a different ticket.

**Blocking.** If the work needs something this instance cannot do, such as
opening Moho or a decision from the user, set `status: blocked`, say exactly
what is needed in the log, and set `needs` to who can unblock it.

**Finishing.** Set `status: review` when the outputs exist and `done` only
when the "Done when" condition has been checked. Checked means observed, not
expected.

## The handoff entry

The last log entry of a session is the handoff. It has to let a cold reader
continue without asking anything:

```markdown
- 2026-11-12 cloud: Wrote score v2 for shot 010 (frames 1-195).
  Changed: shots/010/score.json, shots/010/anim.moho.
  Verified: apply ran clean; structural diff shows only the 14 targeted channels changed.
  Not verified: nothing rendered yet, so the motion is unseen.
  Next: render frames 1, 24, 48, 77, 115, 187 from anim.moho on the local
  machine, tile them, attach to this ticket. Needs: local-moho.
```

Five parts, every time: what was done, what changed, what was verified and
how, what was not, the next step and who can take it.

## Journal

`pipeline/journal/<date>-<slug>.md`, one per session that learned something
worth keeping. This is the long-term memory: not what was done (the tickets
and git log have that) but why, what surprised, and what the user said she
wanted. Write the context along with the conclusion. "Use Kokoro" is a rule
that rots; "Kokoro, because it is Apache-licensed and ran on CPU in the
sandbox, at a time when the alternative was non-commercial" can be re-checked
when circumstances change.

Keep personal details about the user out of it. The repo may be public.

## Standing decisions

`pipeline/README.md` lists decisions the user has made. Do not reopen them in
passing. An instance that thinks one is wrong says so in a ticket with its
evidence and lets her decide.

## Disagreeing with earlier work

Do not silently redo another instance's work. Note the problem in the ticket
log with evidence, fix it there if it is in the current lane, or open a ticket
for the lane that owns it. Anything recorded as a caution about destructive or
irreversible actions stays in force until the user lifts it.

## Git

- Small commits with messages that say what changed and why.
- Pull before starting; push before ending the session.
- Follow the branch instructions of the session being run in. Cloud sessions
  are usually given their own branch.
- `.moho` files are binary. Two sessions must not edit the same one; the
  ticket's `outputs` list is the lock. Saving rigs as `.mohoproj` makes them
  diffable text, at the cost of losing the single-file convenience.
- Rendered frames and audio caches are large and reproducible. Keep them out
  of git unless a ticket's review needs a specific contact sheet.

## Chat sessions without repo access

The user pastes or attaches the ticket and the relevant files. The chat
session's result comes back as text she hands to a repo-capable session, which
commits it and logs the handoff. The chat session should write its output in
the target file's format so nothing needs translating.

## Putting this skill on every surface

The skill is a folder: `SKILL.md`, `references/`, `scripts/`. In a repo
checkout it loads from `.claude/skills/animation-pipeline/`. For chat, package
the folder as a `.skill` file and install it from the app's skill settings.
Keep the repo copy as the source and re-package after changes, so every
surface is working from the same instructions.
