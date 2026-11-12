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
| 2026-11-12 | 3D is occasional: small assets rendered with shaders applied, brought into Moho as images. No 3D shots | User, follow-up to kickoff |
| 2026-11-12 | "Reusable assets" means ordinary reuse of her own work: an environment used in more than one scene, recurring props, tileable textures such as flowers and moss | User, second follow-up |
| 2026-11-12 | Prefer free and open-source tools; reuse existing ones before writing new ones | User preference |

## Facts about the setup

Stated by the user, not inferred.

- Her own machine has paid licenses, not educational ones.
- Educational licenses are on the school's machines, and on a student account
  she occasionally signs into at home.
- Maya at home is 2025.3; the school runs 2026.

Working rule that follows, proposed by a session and not yet confirmed by
her: assets for the channel are made under the personal licenses, and work
done while signed into the student account stays out of monetized videos.

## Open questions for the user

- Which RenderMan edition is installed at home (its free edition is
  non-commercial)
- What the first show is (T-0005)
- Whether the installed Moho is 14.4 or 14.5

## Assumptions that turned out wrong

Kept so they are not made again.

- "She is a student, so her tools are student licenses." No. See above.
- "Organic looking means disguising automation." No. It names the 2D look.
- "Reusable assets raises a sameness problem." No. It is normal reuse of sets,
  props and textures.
