# Research notes, November 2026

What was found while planning the pipeline, how each finding was established,
and where it came from. "Tested" means run in the cloud sandbox on 2026-11-12.
"Read" means taken from a source without running anything.

The sandbox could reach GitHub and PyPI but not lostmarble.com,
renderman.pixar.com, support.google.com or the Deadline documentation, so
several official pages are represented only by search summaries. Those items
are marked.

## Moho

| Finding | Basis |
|---|---|
| `.moho` is a ZIP of `Project.mohoproj` (JSON) and `preview.jpg` | Tested on `CharWalk.moho` from [godot_moho_importer](https://github.com/jpdurigan/godot_moho_importer) |
| Every animatable property is a channel of parallel `when` / `val` / `interp` lists; frame 0 is the rest pose; angles in radians | Tested, same file |
| Interpolation codes 0 to 11 (linear, smooth, ease, step, noisy, cycle, pose, ease in, ease out, bezier, bounce, elastic) | Read from the importer's source; its author states they match Moho |
| Smart bones are actions named after a bone, stored per channel under `actions` | Tested, same file (`Eyes_LR`, `Eyes_UD`) |
| Switch layers store the active child in a `switch_keys` channel | Read from the importer's source; the sample has no switch layer |
| Moho writes decimals with at most six places and no exponents | Tested: a serializer following that rule reproduces the file byte for byte |
| Moho 13 opens and saves bare `.mohoproj`; `.moho` files are not mergeable in git | Read: [moho-template](https://github.com/definitelyokay/moho-template) |
| Moho 14 embeds Lua 5.4; 12 to 13.5 used Lua 5.2; "Print Moho API" lists the scripting interface | Search summary of [mohoscripting.com](https://mohoscripting.com/) |
| Command-line render: `-r file`, with `-o` and `-f`; reports of the output flags failing | Search summary of Lost Marble forum threads ([one](https://lostmarble.com/forum/viewtopic.php?p=212186), [two](https://www.lostmarble.com/forum/viewtopic.php?p=213392)) |
| Moho 14.4 (Nov 2025) exports rigs and animation as glTF/GLB | Search summary: [Lost Marble](https://moho.lostmarble.com/blogs/news/free-update-export-to-video-game-engines-with-the-moho-14-4-side-quest), [Digital Production](https://digitalproduction.com/2025/11/14/moho-14-4-goes-on-a-side-quest-2d-meets-game-engines/) |
| Moho 14.5 (Oct 2026) records webcam and gamepad performances as keyframes | Search summary: [Digital Production](https://digitalproduction.com/2026/10/21/moho-14-5-showtime-live-animation/) |
| Moho Pro 14 is a perpetual license at USD 399.99 | Search summary of the same article. Commercial-use wording not found |

The sample file is version 1038, from 2022. No Moho 14 file has been
inspected. That is ticket T-0001.

## Voice and lip-sync

| Finding | Basis |
|---|---|
| Rhubarb Lip Sync 1.14.0 runs on Linux, exports Moho switch data with `-f dat`, Preston Blair names with `--datUsePrestonBlair` | Tested; [repository](https://github.com/DanielSWolf/rhubarb-lip-sync) |
| Rhubarb is MIT and its license says the output belongs to the user | Read from `LICENSE.md` in the release |
| Kokoro via `kokoro-onnx` 0.6.1 synthesizes faster than real time on CPU with the int8 model; 54 voices | Tested; [kokoro-onnx](https://github.com/thewh1teagle/kokoro-onnx) |
| Kokoro is Apache 2.0; Chatterbox MIT; Coqui XTTS v2 non-commercial; Piper moved to a GPL codebase; Orpheus unclear | Search summaries: [tts.ai guide](https://tts.ai/blog/open-source-text-to-speech-guide-2026/), [Picovoice benchmark](https://picovoice.ai/blog/on-device-tts/). Not checked against model cards |
| Hugging Face is not reachable from the sandbox, so Piper voices could not be fetched; Kokoro's files come from GitHub releases and could | Tested |

## 3D tools and licenses

| Finding | Basis |
|---|---|
| Educational Maya is limited to learning, training and research | Search summary; consistent across sources |
| Maya Indie permits commercial work under USD 100k revenue, is not sold in every country, and is listed around USD 300 to 330 a year | Search summary: [Autodesk](https://www.autodesk.com/campaigns/me-indie/maya-indie), [pricing guide](https://www.foxrenderfarm.com/share/how-much-does-maya-cost/). Price not confirmed with Autodesk |
| RenderMan Non-Commercial is for personal projects, research and tool development | Search summary: [Pixar FAQ](https://renderman.pixar.com/general-faq), [CG Channel](https://www.cgchannel.com/2026/07/download-the-free-edition-of-renderman-27/) |
| RenderMan 27 made XPU final-frame ready and supports Stylized Looks in XPU; 27.3 added MaterialX in XPU | Search summary: [Digital Production](https://digitalproduction.com/2026/08/04/renderman-27-3-adds-materialx-to-xpu/) |
| Whether the non-commercial edition includes Stylized Looks | Conflicting reports between 27.0 and 27.3 coverage. Unresolved |
| Open-source MCP servers exist for driving Maya through its commandPort | Search summary: [maya-mcp](https://pypi.org/project/maya-mcp/). Not evaluated |

## YouTube

| Finding | Basis |
|---|---|
| "Repetitious content" became "inauthentic content" in July 2025 | Search summary: [AlternativeTo](https://alternativeto.net/news/2025/7/youtube-updates-its-policy-to-demonetize-inauthentic-mass-produced-ai-generated-content) |
| July 2026 clarification names three demonetized categories: generic or template-based, distressing, and AI personas on sensitive topics | Search summary: [TechCrunch](https://techcrunch.com/2026/07/20/youtube-clarifies-policies-around-ai-slop-and-upsetting-videos/), [Tubefilter](https://www.tubefilter.com/2026/07/13/youtube-inauthentic-content-monetization-policy-update/), [Metricool](https://metricool.com/youtube-ai-content-rules-monetization/) |
| AI assistance and synthetic narration are not banned in themselves | Same sources |
| Clearly unrealistic content such as animation is exempt from the synthetic-content label | Search summary: [AIR Media-Tech](https://air.io/en/youtube-hacks/youtube-ai-disclosure-in-2026-label-it-yourself-or-youtube-will) |
| Partner Program: 1,000 subscribers and 4,000 hours, or 10M Shorts views in 90 days; thresholds reportedly double for new applicants from 1 February 2027 | Search summary: [AIR Media-Tech](https://air.io/en/monetization/youtube-partner-program-requirements-2026-the-complete-guide), [PPC Land](https://ppc.land/new-youtube-creators-face-8-000-hour-bar-for-ad-revenue-from-february-2027/) |
| API uploads from unverified projects are locked to private until the project is audited | Search summary quoting Google's `videos.insert` reference: [guide](https://postproxy.dev/blog/youtube-upload-api-guide/), [issue thread](https://github.com/porjo/youtubeuploader/issues/86) |

None of the YouTube rows were read from YouTube's own pages. Check the Help
Center before acting on thresholds or policy wording.

## Assistant coordination

Claude Code has an experimental "agent teams" mode with a shared task list
([docs](https://code.claude.com/docs/en/agent-teams)). It coordinates agents
inside one running session. The instances on this project run on different
surfaces at different times, so the protocol here uses files in the repo
instead and does not depend on that feature.

## Observations that did not fit elsewhere

- During Kokoro synthesis something attempted a connection to a Microsoft
  telemetry host. The sandbox blocked it. Not traced to a specific package.
- `git lfs` objects in public repositories are not served to the sandbox, so
  sample projects stored that way arrive as pointer stubs. The sample used
  here is committed directly.
