---
name: crun-cover-generator
description: Generate high-impact video covers, thumbnails, script posters, title banners, or social media video thumbnails (YouTube 16:9, Bilibili 16:9, Xiaohongshu 3:4/9:16, TikTok 9:16, Douyin 9:16) from a video file/URL, video script, outline, storyboard, or title concept using Crun AI image models. Triggers on requests like video thumbnail generator, script to cover image, video cover poster, YouTube thumbnail creation, Xiaohongshu video cover, Bilibili thumbnail, video script title poster, video frame to cover — even without naming Crun or a specific model.
---

# Crun Video & Script Cover Generator

Use this skill to extract central visual themes, core narrative hooks, and emotional highlights from a video file/URL, video script, storyboard, or title concept, and transform them into high-contrast, click-worthy video covers and thumbnails using Crun AI image models.

Use `../../../runtime/crun_cli.py`, `../../../catalog/models.json`, and the shared child skills:

- `../../crun-model-router/SKILL.md` — model routing & live schema inspection
- `../../crun-account-credits/SKILL.md` — balance & affordability estimation
- `../../crun-task-runner/SKILL.md` — task creation, monitoring, recovery, result delivery (the authority)

---

## Trigger

Activate for any request involving: generating video covers, video thumbnails, script title posters, YouTube thumbnails, Xiaohongshu (RED) video covers, Bilibili thumbnails, TikTok/Douyin covers, or turning video files/scripts into cover media — e.g., `crun-cover-generator`, video to cover, script to thumbnail, video poster generator, YouTube thumbnail creator, video title banner — even if the user never mentions "Crun" or a specific model name.

---

## Execution Workflow

```text
[ User Request ] (Video File/Link OR Script/Text + Target Platform/Style)
    │
    ├── 1. Input Analysis & Visual Concept Extraction
    │       ├─ Video Source (File/URL): Extract/upload keyframe frame → python <runtime>/crun_cli.py upload <local-file>
    │       └─ Script Source (Text/Outline): Extract core narrative hook, primary subject, emotional contrast, & title text
    │
    ├── 2. Target Platform & Format Resolution
    │       ├─ Target Aspect Ratio (16:9 for YouTube/Bilibili; 3:4 or 9:16 for Xiaohongshu/TikTok; 1:1 for Feeds)
    │       └─ Cover Visual Style (Cinematic Poster, High-Contrast Clickbait, Minimalist Tech, 2D Anime/Comic, Vlog Warm)
    │
    ├── 3. Model Routing & Prompt Engineering
    │       ├─ Pick Image Model: Reference-Driven (I2I) if video frame uploaded vs Text-Driven (T2I) if script/text source
    │       ├─ Synthesize structured visual prompts in English with dedicated title composition space
    │       └─ Inspect live schema: python <runtime>/crun_cli.py models describe --model <model>
    │
    ├── 4. Estimate & Confirmation Gate
    │       ├─ Estimate credits (crun-account-credits): task estimate --model <model> --input-file <input.json>
    │       └─ Present extracted cover concept & task summary → Require explicit user OK before spending
    │
    └── 5. Task Creation & Result Delivery (crun-task-runner)
            ├─ Create task: python <runtime>/crun_cli.py task create --model <model> --input-file <input.json>
            ├─ Poll status: python <runtime>/crun_cli.py task wait --task-id <task_id>
            └─ Deliver local media path, inline image preview, and layout/typography recommendations for title text
```

---

## Step 1 — Input Analysis & Visual Concept Extraction

Identify the input source type:

### Case A: Video File, Video Link, or Keyframe Image
1. **Keyframe Extraction / Media Upload**:
   - If the user provides a video file or screenshot, upload it via `python <runtime>/crun_cli.py upload <file>` to obtain a Crun `file_url`.
   - If the user provides a video link (e.g. Bilibili, YouTube, web page), analyze page/video info (`read_url_content`, `search_web`), extract the main visual theme, title, and key screenshots if accessible.

2. **Visual Focus Identification**:
   - Identify main character, core object, or central action scene.
   - Determine key emotional tone (shocking, inspiring, dramatic, educational, humorous).

### Case B: Video Script, Storyboard, Outline, or Title Concept
1. **Narrative & Hook Extraction**:
   - Extract **Core Subject/Protagonist**: Central figure, product, or scenario.
   - Extract **Headline / Title Hook**: The main text overlay phrase (e.g., "3 Mins to Master AI", "Unbelievable Truth!").
   - Extract **Climactic Scene**: The most visually arresting moment described in the script.

---

## Step 2 — Target Platform & Style Resolution

If aspect ratio, platform, or style is not specified, present options via interactive buttons (`AskUserQuestion`):

1. **Target Platform & Aspect Ratio**:
   - **16:9 (Horizontal)**: YouTube Thumbnail, Bilibili Cover, Web Video Banner.
   - **3:4 (Vertical - Recommended for Xiaohongshu)**: Xiaohongshu (RED) Cover, WeChat Video Channel.
   - **9:16 (Vertical)**: TikTok, Douyin, YouTube Shorts, Instagram Reels.
   - **1:1 (Square)**: Instagram Feed, Podcast Cover, Square Feed.

2. **Visual Cover Style**:
   - **High-Contrast Clickbait**: Vibrant bold colors, dramatic expressions, high subject contrast, intense lighting, composition space for huge bold title text.
   - **Cinematic Movie Poster**: Deep shadows, anamorphic lens flare, atmospheric atmosphere, film color grading.
   - **Modern Tech / Minimalist**: Clean layout, 3D render aesthetics, sleek metallic/neon accents, elegant background depth.
   - **2D Anime / Comic Style**: Bold line art, cel-shaded coloring, expressive anime aesthetic, dynamic action lines.
   - **Vlog / Realist Warm**: Warm natural lighting, authentic lifestyle setting, soft background bokeh.

---

## Step 3 — Model Routing & Prompt Generation

### Model Routing Matrix

Select the optimal model based on input type and task requirements:

| Input Source | Preferred Models (Text-Driven T2I) | Preferred Models (Reference-Driven I2I / `supports_reference: true`) | Key Advantages |
|---|---|---|---|
| **Script / Text Outline** | `bytedance/seedream-5-pro`, `openai/gpt-image-2-premium`, `qwen-image-3.0-pro` | N/A | High prompt fidelity, crisp composition, strong artistic styling |
| **Video Frame / Image Reference** | N/A | `bytedance/seedream-5-pro`, `qwen-image-edit-2.0-pro`, `google/nano-banana-pro` | Preserves character identity, pose, and original scene lighting while enhancing cover aesthetics |

### Prompt Structure (English)

Construct prompts in structured English for maximum visual fidelity, ensuring composition leaves clear space (e.g. left side, upper third) for title text overlays:

- **Script-Based Cover Prompt Template**:
  `A high-impact, click-worthy video cover for a video titled "[TITLE_HOOK]". Visual scene depicting [CLIMACTIC_SCENE_DESCRIPTION]. Style: [VISUAL_COVER_STYLE]. Feature a prominent [CORE_SUBJECT] with intense [EMOTIONAL_TONE] expressions. Professional lighting with strong rim light and shallow depth of field. Designed with clean composition space on the [LEFT/TOP] side for title text overlay. 8k resolution, cinematic composition.`

- **Video-Frame-Based Cover Prompt Template**:
  `A professional video thumbnail remake based on reference image. Transform scene into a high-contrast [VISUAL_COVER_STYLE] video cover. Enhance subject details of [CORE_SUBJECT], vivid color grading, dramatic studio lighting, sharp focus, clean background separation. Reserved space for large bold cover text.`

Inspect live model schema before payload creation:

```text
python <root>/runtime/crun_cli.py models describe --model <model>
```

---

## Step 4 — Credit Estimate & Confirmation Gate

Read `../../crun-account-credits/SKILL.md`. Estimate payload costs:

```text
python <root>/runtime/crun_cli.py task estimate --model <model> --input-file <input.json>
```

Require `affordable: true`. Present confirmation summary card:

- **Source Type**: `[Video Frame / Script]`
- **Target Platform**: `[YouTube / Bilibili / Xiaohongshu / TikTok / etc.]`
- **Aspect Ratio**: `[16:9 / 3:4 / 9:16 / 1:1]`
- **Cover Style**: `[Selected Visual Style]`
- **Title Hook**: `"[TITLE_HOOK]"`
- **Selected Model**: `[MODEL_NAME]`
- **Estimated Cost**: `[CREDITS]`

Wait for explicit user confirmation via interactive buttons before creating task.

---

## Step 5 — Create & Deliver

Read `../../crun-task-runner/SKILL.md` for task lifecycle authority:

```text
python <root>/runtime/crun_cli.py task create --model <model> --input-file <input.json>
python <root>/runtime/crun_cli.py task wait --task-id <task_id> --timeout-seconds 120
```

---

## Delivery Format

Deliver the completion response with metadata, cover image preview, and text layout suggestions:

```text
✅ Video cover generation completed!
- Task ID: <task_id>
- Target Platform: <Platform> (<Aspect Ratio>)
- Cover Style: <Style>
- Model: <model>
- Credits Spent: <credits>
- Output File Path: <local_media_path>

[Inline Preview of Cover Image]

💡 **Title Text Overlay Recommendations**:
- **Main Hook Text**: "<TITLE_HOOK>" (Recommended font: Bold Sans-Serif / Heavy Impact Font, Color: Yellow/White with black stroke)
- **Positioning**: Place text on the <left/top> high-contrast negative space of the cover image.
```
