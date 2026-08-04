---
name: crun-meme-generator
description: Generate static image memes/stickers (静态表情包) and animated GIF memes/reaction emojis (动态 GIF 表情包) using Crun image and video models. Use whenever the user asks for a meme, sticker, reaction emoji, 表情包, 静态表情包, 动态表情包, GIF表情包, reaction GIF, funny reaction animation, or requests adding text/stickers to images or converting short generated videos into GIF memes — even if they don't explicitly say "Crun".
---

# Crun Meme & Emoji Generator

Use this skill to generate static image memes/stickers (静态表情包) and animated GIF reaction memes (动态 GIF 表情包) via Crun AI models.

- **Static Memes (静态表情包)**: Route to Crun image generation models (`modality: "image"`), set appropriate resolution/aspect ratio, generate image, and output PNG/JPG.
- **Animated GIF Memes (动态 GIF 表情包)**: Route to fast Crun video generation models (`modality: "video"`), default to the model's **lowest resolution** (e.g. `480p` / `720p`), generate pure visual motion (without asking video AI model to render text to avoid text garbling/乱码), download MP4, and add crisp text overlay directly onto the GIF via `scripts/video_to_gif.py --text "配文"`.
- **Interactive Button Confirmation (按钮式二次确认)**: For both static and GIF memes, always present the confirmation details (including Model, Credits, Visual Style, Text Caption, and Resolution) and use **interactive option buttons** (e.g. `ask_question` tool) for user confirmation before task creation.

---

## Workflow Overview

Follow this end-to-end execution flow for all meme and emoji generation requests:

```text
User Request (Meme/Emoji/GIF)
   │
   ├── 1. Determine Format (Static Image vs Animated GIF)
   │
   ├── 2. Upload Input Media (If user provides reference photo/image)
   │       └─ python <root>/runtime/crun_cli.py upload <local-file>
   │
   ├── 3. Route Model & Construct Payload
   │       ├─ Static Image: modality="image", define Visual Style & Resolution
   │       └─ Animated GIF: modality="video", lowest resolution default, purely visual motion prompt (no text in video prompt)
   │
   ├── 4. Estimate Affordability & Present Button Confirmation (按钮式二次确认)
   │       ├─ Estimate: python <root>/runtime/crun_cli.py task estimate --model <model> --input-file <input.json>
   │       └─ Ask Question: Interactive option buttons (包含风格、配文、分辨率、模型与额度)
   │
   ├── 5. Create Task & Poll Status (crun-task-runner)
   │       ├─ python <root>/runtime/crun_cli.py task create --model <model> --input-file <input.json>
   │       └─ python <root>/runtime/crun_cli.py task wait --task-id <task_id> --timeout-seconds 120
   │
   └── 6. Final GIF Conversion with Direct Text Overlay
           └─ python <skill-root>/skills/crun-meme-generator/scripts/video_to_gif.py <video-path> --text "配文" --output <gif-path>
```

---

## Detailed Execution Steps

### 1. Identify Format and Intent

- **Static Image Meme (静态表情包)**:
  - User phrases: "做个表情包", "画个表情包", "静态表情包", "搞笑图片", "生成搞笑表情包".
  - Output target: PNG / JPG image file.
  - Operation: `text-to-image` (new meme) or `image-edit` (modifying or adding caption to an existing photo).

- **Animated GIF Meme (动态 GIF 表情包)**:
  - User phrases: "做个GIF表情包", "动态表情包", "动图表情包", "搞笑GIF", "把这个转成GIF表情".
  - Output target: GIF file.
  - Operation: `text-to-video` (new animated GIF) or `image-to-video` (animating a reference photo into a GIF).

---

### 2. Upload Reference Media (If Provided)

When the user provides a local reference photo (e.g. face photo, pet photo, existing image to turn into meme/GIF):

```text
python <skill-root>/runtime/crun_cli.py upload <local-file>
```

Use the returned `file_url` in the model payload. Never send raw local paths or Base64 into Crun model inputs.

---

### 3. Route Model and Build Payload

Read `skills/crun-model-router/SKILL.md` to construct routing intent:

```json
{
  "modality": "image|video",
  "operation": "text-to-image|image-edit|text-to-video|image-to-video",
  "quality": "balanced",
  "speed": "fast"
}
```

#### A) Static Image Meme Defaults & Style Specification
- Preferred models: `openai/gpt-image-2`, `bytedance/seedream-5-pro`, `google/nano-banana-pro`, `qwen-image-2.0-pro`.
- **Visual Style (图片风格)**: Explicitly choose or confirm a visual style:
  - Examples: `3D Q版卡通风格` (3D cartoon sticker), `写实真人风格` (Realistic reaction photo), `魔性手绘风格` (Funny doodle/sketch), `二次元动漫风格` (Anime reaction), `像素风` (Pixel art meme).
  - Explicitly include style details in the prompt (e.g. `"cute 3D cartoon style sticker with white outline..."`).
- **Resolution & Aspect Ratio (分辨率与比例)**:
  - Default to square `1:1` aspect ratio or `1K` resolution suitable for memes.

#### B) Animated GIF Meme Defaults & Text Overlay Strategy
- Preferred fast video models: `bytedance/seedance2-0-fast-t2v` / `bytedance/seedance2-0-fast-i2v`, `bytedance/seedance1-0-pro-fast-t2v`, `vidu/q3-turbo-t2v`, `kling/v3-turbo`.
- **Lowest Resolution Default (默认最低分辨率)**:
  - Inspect model schema with `crun_cli.py models describe --model <model>`.
  - **Always select the lowest resolution supported by that model** (e.g. `480p` or `720p` or lowest enum value). Lower resolution generates faster, uses fewer credits, and reduces GIF file size.
- **Avoid Text in AI Video Prompt (解决视频模型文字乱码)**:
  - **Do NOT ask the video AI model to generate text inside the video prompt** because video models frequently distort text into unreadable gibberish.
  - Focus the video AI prompt purely on visual character, facial expression, and action (e.g. `"cute 3D cartoon cat looking shocked, funny looping reaction motion, clean background"`).
- **Text Caption & Multilingual Adaptation (转成 GIF 时直接渲染清晰文字)**:
  - Default to a funny/expressive text caption matching the user's language:
    - Chinese context: `"摸鱼中..."`, `"收到！"`, `"满脑子都是放假"`, `"开摆"`, `"打工人打工魂"`.
    - English context: `"Monday Mood"`, `"BRB Slapping Alarm"`, `"Approved!"`, `"On My Way"`.
  - Pass the caption to `video_to_gif.py` via `--text "<caption_text>"`. The converter script overlays crisp, stroke-bordered text directly onto the GIF frames.
- Set short duration (e.g. 2-5 seconds).

---

### 4. Estimate Affordability & Button Confirmation Gate (按钮式二次确认)

Read `skills/crun-account-credits/SKILL.md`:

```text
python <skill-root>/runtime/crun_cli.py task estimate --model <model> --input-file <input.json>
```

Verify `affordable: true`. Before calling `task create`, **call `ask_question` tool to present an interactive choice modal with confirmation buttons**.

#### Mandatory Confirmation Content (确认内容规范):

1. **For Static Image Memes (静态表情包确认内容)**:
   - **模型名称 (Model)**: e.g. `bytedance/seedream-5-pro`
   - **预估消耗额度 (Estimated Credits)**: e.g. `2.5 额度`
   - **图片风格 (Visual Style)**: e.g. `3D Q版卡通风格（带白色描边）`
   - **文字配文 (Text Caption)**: e.g. `“周一的我”`
   - **分辨率与比例 (Resolution)**: e.g. `1K (1:1 正方形)`

2. **For Animated GIF Memes (动态 GIF 表情包确认内容)**:
   - **模型名称 (Model)**: e.g. `bytedance/seedance2-0-fast-t2v`
   - **预估消耗额度 (Estimated Credits)**: e.g. `4.0 额度`
   - **画面风格 (Visual Style)**: e.g. `3D 卡通魔性表情包风格`
   - **文字配文 (Text Caption)**: e.g. `“摸鱼中...” (将在转GIF时叠加高清描边字幕，避免AI视频文字乱码)`
   - **分辨率 (Resolution)**: e.g. `480p（已选择模型的最低分辨率，生成最快且最节省额度）`
   - **视频时长 (Duration)**: e.g. `3秒（转为 12fps 循环 GIF）`

#### Interactive Confirmation Buttons (按钮交互方式):
Use `ask_question` tool to prompt the user with selectable options:
- Option 1: `"确认按此参数生成 (Confirm & Generate)"`
- Option 2: `"修改配文或风格 (Modify Caption/Style)"`
- Option 3: `"取消生成 (Cancel)"`

---

### 5. Create Task and Wait for Download

Read `skills/crun-task-runner/SKILL.md`:

```text
python <skill-root>/runtime/crun_cli.py task create --model <model> --input-file <input.json>
python <skill-root>/runtime/crun_cli.py task wait --task-id <task_id> --timeout-seconds 120
```

When task completes, `crun_cli.py` automatically downloads the result media to `~/.crun/output/yyyy-mm-dd/<task_id>/`.

---

### 6. Convert Video to GIF with Direct Text Overlay

Invoke `video_to_gif.py` with `--text` parameter to overlay the caption directly onto the GIF frames:

```text
python <skill-root>/skills/crun-meme-generator/scripts/video_to_gif.py <video-path> --output <gif-path> --fps 12 --width 480 --text "摸鱼中..." --text-position bottom
```

**Parameters for `video_to_gif.py`**:
- `<video-path>`: Path to the downloaded MP4 video file.
- `--output` / `-o`: Output path for the converted `.gif` file.
- `--fps`: Target frame rate (default: `12` - optimal for reaction memes).
- `--width`: Target width scaling in pixels (default: `480` - standard meme dimensions).
- `--text` / `-t`: Text caption to overlay directly onto the GIF (supports Chinese/English CJK stroke text).
- `--text-position`: Position of caption overlay (`bottom`, `top`, or `center`).

The script returns JSON output:
```json
{
  "code": 0,
  "status": "success",
  "input_file": "/path/to/video.mp4",
  "output_file": "/path/to/meme.gif",
  "size_bytes": 1425600,
  "fps": 12,
  "width": 480,
  "text_overlay": "摸鱼中...",
  "text_position": "bottom",
  "conversion_method": "ffmpeg+PIL"
}
```

---

## Confirmation Message & Button Examples

### Example 1: Static Image Meme Button Confirmation (`ask_question`)
```json
{
  "questions": [
    {
      "question": "🎨 已为您选定图片表情包生成方案，请确认：\n- 模型: bytedance/seedream-5-pro\n- 图片风格: 3D Q版卡通风格（带白色描边）\n- 文字配文: “周一的我”\n- 分辨率: 1K (1:1 正方形)\n- 预估消耗: 2.5 额度",
      "options": [
        "确认按此参数生成",
        "修改配文或风格",
        "取消生成"
      ],
      "is_multi_select": false
    }
  ]
}
```

### Example 2: Animated GIF Meme Button Confirmation (`ask_question`)
```json
{
  "questions": [
    {
      "question": "🎬 已为您选定动态 GIF 表情包生成方案，请确认：\n- 模型: bytedance/seedance2-0-fast-t2v\n- 画面风格: 3D 卡通魔性表情包风格\n- 文字配文: “摸鱼中...” (转GIF时叠加描边字幕，防乱码)\n- 分辨率: 480p（模型最低分辨率，生成最快且节省额度）\n- 视频时长: 3秒（转 12fps 循环 GIF）\n- 预估消耗: 4.0 额度",
      "options": [
        "确认按此参数生成",
        "修改配文或风格",
        "取消生成"
      ],
      "is_multi_select": false
    }
  ]
}
```

---

## Delivery and Preview

Always provide the user with clear execution details and an inline local markdown preview:

```text
✅ 表情包生成成功！
- 任务 ID: <task_id>
- 画面风格: <style>
- 文字配文: <caption_or_none>
- 分辨率: <resolution>
- 消耗额度: <credits>
- 存储路径: <local_gif_or_image_path>

![Meme Preview](/absolute/path/to/meme.gif)
```
