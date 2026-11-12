# Pipeline state

Shared working state for every assistant session and for the user. How to use
it: `.claude/skills/animation-pipeline/references/collaboration.md`.

- `tickets/`: one file per work item
- `journal/`: what sessions learned, with the reasoning

## Standing decisions

Decisions the user has made. Do not reopen these in passing; raise a ticket
with evidence if one looks wrong.

| Date | Decision | Source |
|---|---|---|
| 2026-11-12 | Assets are the user's own work or CC0, and human-made | Kickoff request |
| 2026-11-12 | Assistants rig and animate; the user supplies the art | Kickoff request |
| 2026-11-12 | Mostly Moho, so the show stays 2D and hand-made in look ("organic" is her word for this) | User, follow-up to kickoff |
| 2026-11-12 | 3D is occasional: small assets rendered with shaders applied, brought into Moho as images. No 3D shots | User, follow-up to kickoff. License route still open, see T-0004 |
| 2026-11-12 | Prefer free and open-source tools; reuse existing ones before writing new ones | User preference |

## Open questions for the user

- Which tool renders 3D assets for monetized videos (T-0004). Not urgent: nothing
  is blocked until the first asset is needed
- What the first show is (T-0005)
- Whether the installed Moho is 14.4 or 14.5, and whether it is a standard or
  educational license
