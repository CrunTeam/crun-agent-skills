---
name: crun-product-suite-generator
description: Generate 10 cohesive e-commerce product listing images (hero main shot, key feature callout, lifestyle context, material detail close-up, dimensions/specs, model demo, unboxing/accessories, minimalist studio luxury shot, multi-angle view, promotional sales banner) or product image suites using Crun AI image models. Triggers on requests like generating 10 product images, product listing image kit, e-commerce product suite, 10-packshot set, product showcase grid, Amazon/Shopify/Etsy/E-commerce product image set generator, generating 10-shot suite, product photo suite generator — even without naming Crun or a model.
---

# Crun E-Commerce Product 10-Image Suite Generator

Use this skill to transform product photos, reference images, URLs, or product descriptions into a complete, professional set of 10 e-commerce product images (hero main shot + feature & detail pack) with consistent product identity, lighting, color grading, and high-converting visual compositions using Crun AI image models.

This skill integrates with `../../../runtime/crun_cli.py`, `../../../catalog/models.json`, and the shared core skills:

- `../../crun-model-router/SKILL.md` — model routing & live schema inspection
- `../../crun-account-credits/SKILL.md` — balance & affordability estimation (for 10 tasks)
- `../../crun-task-runner/SKILL.md` — task creation, monitoring, recovery, and result delivery (the authority)

---

## Trigger

Activate whenever the user asks for:
- Generating 10 product images for e-commerce (`10 product images`, `10-shot suite`, `e-commerce 10-pack listing images`)
- Main product listing image kit (main hero + detail listing photos for Amazon, Shopify, Etsy, TikTok Shop, eBay)
- Product image suite generation (`crun-product-suite-generator`, `product photo suite generator`, `multi-angle product set`)
- Generating multi-shot product showcase pack

---

## Workflow Overview

```text
[ User Request ] (Product Photo / Reference Image / Description / URL)
    │
    ├── 1. Product Analysis & Reference Upload
    │       ├─ Extract product name, core selling points, key color tone & brand aesthetic
    │       └─ Upload local product reference: python <root>/runtime/crun_cli.py upload <local-file>
    │
    ├── 2. 10-Shot Composition & Visual Prompt Plan
    │       ├─ Structure standard 10-shot suite (Main, USP, Lifestyle, Detail, Specs, Model, Unboxing, Studio, Multi-Angle, Promo)
    │       └─ Synthesize 10 English visual prompts with product consistency anchors
    │
    ├── 3. Model Routing & Schema Inspection
    │       ├─ Pick image model (T2I or I2I reference-driven): bytedance/seedream-5-pro, qwen-image-edit-2.0-pro, etc.
    │       └─ Inspect live schema: python <root>/runtime/crun_cli.py models describe --model <model>
    │
    ├── 4. Account Credits Estimation & Confirmation Gate
    │       ├─ Estimate 10 tasks: python <root>/runtime/crun_cli.py task estimate --model <model> --input-file <input.json>
    │       └─ Present interactive button gate (ask_question) with 10-shot breakdown & total cost estimate
    │
    ├── 5. Parallel Batch Task Execution (crun-task-runner)
    │       ├─ Batch create tasks: python <root>/runtime/crun_cli.py task create --model <model> --input-file <input_i.json>
    │       └─ Poll status until completion: python <root>/runtime/crun_cli.py task wait --task-id <task_id_i>
    │
    └── 6. Grid Composite Stitching & Final Delivery
            ├─ Stitch 10 images into overview grid: python <skill-root>/scripts/stitch_product_grid.py <paths...> --grid 5x2
            └─ Deliver 10 individual image paths + composite grid preview card
```

---

## Detailed Execution Steps

### Step 1 — Product Analysis & Reference Upload

1. **Extract Core Product Profile**:
   - **Product Name & Category**: e.g., Wireless ANC Headphones, Matte Ceramic Coffee Tumbler, Ergonomic Office Chair.
   - **Key Visual Features**: Material (brushed aluminum, matte silicone), color scheme (space gray, sage green), shape highlights.
   - **Core Selling Points**: Active Noise Cancellation, 40-hour battery life, ergonomic memory foam, IPX7 waterproof.

2. **Upload Reference Media (If Provided)**:
   If the user provides a product photo or reference image:
   ```bash
   python <root>/runtime/crun_cli.py upload <local-file>
   ```
   Use the returned Crun `file_url` as `image_url` or `reference_image` in image-edit payload operations (`operation: "image-edit"`).

---

## Step 2 — 10-Shot Composition & Visual Prompt Plan

Structure the 10 images into the standard high-converting e-commerce product suite:

| Shot # | Shot Category | Visual Focus & Composition | Default Aspect | Visual Prompt Anchor Focus |
|---|---|---|---|---|
| **01** | **Hero Main** | Clean white or neutral gradient background, crisp studio lighting, hero front 3/4 angle | 1:1 / 3:4 | Crisp product silhouette, centered hero composition, studio lighting |
| **02** | **USP Callout** | Close/mid shot highlighting core feature (e.g. glowing touch controls, waterproof splash) | 1:1 / 3:4 | Highlight feature action, dynamic lighting glow, clean focus |
| **03** | **Lifestyle** | Placed in authentic usage environment (coffee shop, modern desk, outdoor gym, cozy bedroom) | 3:4 / 16:9 | Warm ambient lighting, contextual background blur, aesthetic placement |
| **04** | **Craftsmanship** | Macro close-up on premium material texture, stitching, metallic bevel, logo engraving | 1:1 / 3:4 | Extreme detail close-up, shallow depth of field, tactile surface texture |
| **05** | **Dimensions** | Product angled alongside subtle spatial scale anchors (desk accessories, hand scale, clean line background) | 1:1 / 3:4 | Clear spatial perspective, clean background, balanced proportion |
| **06** | **Model Demo** | Human model wearing/holding/using product, demonstrating ergonomic fit and real-world scale | 3:4 / 9:16 | Lifestyle model interaction, natural skin lighting, authentic expression |
| **07** | **Unboxing** | Neat flat-lay arrangement of product, luxury gift box, charging cable, manual, accessories | 1:1 / 3:4 | Flat-lay top view, symmetrical layout, crisp unboxing presentation |
| **08** | **Studio Luxury** | Dramatic rim lighting, dark slate / marble backdrop, sleek shadows, high-end luxury feel | 1:1 / 3:4 | Dramatic key & rim light, deep contrast, premium luxury studio mood |
| **09** | **Multi-Angle** | Side view, rear view, or side-by-side colorway variant comparison | 1:1 / 3:4 | Multi-angle view, clean alignment, color variance showcase |
| **10** | **Promo Banner** | E-commerce festive promotional backdrop (red/gold or holiday gradient, podium display) | 3:4 / 16:9 | E-commerce banner layout, festive luxury podium, eye-catching visual accent |

#### Visual Prompting Principles:
- Construct visual prompts in **English**.
- Include consistent product descriptions across all 10 prompts to maintain product identity.
- Do **NOT** ask AI image models to render text inside images; keep prompts purely visual.

---

## Step 3 — Model Routing & Schema Inspection

Read `../../crun-model-router/SKILL.md` for routing guidelines:

- **Preferred Text-Driven Models**: `bytedance/seedream-5-pro`, `openai/gpt-image-2-premium`, `qwen-image-3.0-pro`, `flux/flux-1-dev`.
- **Preferred Reference-Driven Models (`supports_reference: true`)**: `bytedance/seedream-5-pro`, `qwen-image-edit-2.0-pro`, `google/nano-banana-pro`.

Inspect model schema before building payloads:
```bash
python <root>/runtime/crun_cli.py models describe --model <model>
```

---

## Step 4 — Account Credits Estimation & Execution Gate

Read `../../crun-account-credits/SKILL.md`. Estimate total credits for 10 images:

```bash
python <root>/runtime/crun_cli.py task estimate --model <model> --input-file <sample_input.json>
```

Verify `affordable: true`.

#### Non-Blocking Execution Policy:
1. **Interactive Confirmation (If Supported)**: If the client environment supports interactive question tools (`ask_question` or `AskUserQuestion`), present the confirmation modal.
2. **Seamless Auto-Proceed (Default)**: If interactive question tools are unavailable, or if the user's initial prompt explicitly requested generating the product suite, display the summary card in chat and **immediately proceed to Step 5 (Batch Task Creation & Runner)**. Never halt or block execution indefinitely waiting for user confirmation.

#### Estimation Summary Card:
- **Product Name**: `[PRODUCT_NAME]`
- **Model Selected**: `[MODEL_NAME]`
- **Estimated Total Cost**: `10 images x [CREDITS_PER_IMG] = [TOTAL_CREDITS] Credits`
- **10-Shot Plan Summary**:
  1. `01. Hero Main Shot`
  2. `02. Core Feature (USP Callout)`
  3. `03. Lifestyle Context`
  4. `04. Material & Craftsmanship Detail`
  5. `05. Dimensions & Specs View`
  6. `06. Model Demo & Ergonomic Scale`
  7. `07. Unboxing & Accessories Pack`
  8. `08. Studio Luxury Lighting`
  9. `09. Multi-Angle / Variant View`
  10. `10. Promotional Sales Banner`

---

## Step 5 — Batch Task Creation & Runner

Read `../../crun-task-runner/SKILL.md` for task lifecycle authority. Create 10 tasks and poll status:

```bash
python <root>/runtime/crun_cli.py task create --model <model> --input-file <shot_1.json>
python <root>/runtime/crun_cli.py task wait --task-id <task_id_1> --timeout-seconds 120
```

Collect all 10 downloaded local image file paths: `[shot_1.png, shot_2.png, ..., shot_10.png]`.

---

Invoke `stitch_product_grid.py` to assemble the 10 generated images into a composite 5x2 overview collage card. The script automatically detects and preserves the aspect ratio (e.g. 2:3, 3:4, 1:1, 9:16, 16:9) of input images with zero distortion:

```bash
python skills/scenarios/crun-product-suite-generator/scripts/stitch_product_grid.py \
  shot_1.png shot_2.png shot_3.png shot_4.png shot_5.png shot_6.png shot_7.png shot_8.png shot_9.png shot_10.png \
  --title "[PRODUCT_NAME] — 10-Shot Product Suite" \
  --grid 5x2 \
  --aspect-ratio auto \
  -o product_suite_grid.png
```

---

## Delivery Format

Deliver the completion summary with normalized metadata, 10 individual image links, and inline preview of the composite grid:

```text
✅ 10-Shot E-Commerce Product Suite Generated Successfully!
- Product Name: <product_name>
- Model Used: <model>
- Total Credits Used: <total_credits>
- Grid Layout: 5x2 Overview Collage
- Overview Collage File: <local_grid_path>

### 10 Individual Product Shots:
1. 01. Hero Main: <local_path_1>
2. 02. Core Feature USP: <local_path_2>
3. 03. Lifestyle Context: <local_path_3>
4. 04. Material Detail: <local_path_4>
5. 05. Dimensions View: <local_path_5>
6. 06. Model Demo: <local_path_6>
7. 07. Unboxing & Package: <local_path_7>
8. 08. Studio Luxury: <local_path_8>
9. 09. Multi-Angle View: <local_path_9>
10. 10. Promo Banner: <local_path_10>

![Product Suite 10-Grid Composite Preview](/absolute/path/to/product_suite_grid.png)
```

---

## Canonical User Scenarios & Exemplar Breakdowns

### Scenario 1: Wireless Noise-Canceling Headphones 10-Shot Suite

- **User Intent**: "Generate a complete 10-shot e-commerce product image suite for a pair of minimalist tech wireless noise-canceling headphones."
- **Product Profile**: Matte Space Black Wireless Over-Ear Headphones, brushed aluminum hinges, plush memory foam earcups.
- **Model Selected**: `bytedance/seedream-5-pro`
- **10-Shot Visual Prompts**:
  1. `Shot 01 (Main Hero)`: Centered hero product shot of matte space black wireless headphones on clean soft gray studio pedestal, soft directional lighting, 1:1 ratio.
  2. `Shot 02 (USP Callout)`: Close-up on earcup active noise cancellation touch surface with subtle glowing blue acoustic wave visualization, high tech feeling.
  3. `Shot 03 (Lifestyle)`: Headphones placed on modern oak office desk alongside laptop, warm ambient morning sunlight, blurred background.
  4. `Shot 04 (Material Close-up)`: Extreme macro detail shot of premium hand-stitched leather headband and brushed aluminum hinge texture.
  5. `Shot 05 (Dimensions)`: Headphones next to slim smartphone for scale on clean neutral tabletop, balanced proportion layout.
  6. `Shot 06 (Model Demo)`: Young female model in beige sweater wearing headphones, smiling, listening to music in coffee shop setting.
  7. `Shot 07 (Unboxing)`: Top-down flat lay showing open premium black gift box, headphones, braided USB-C cable, carrying pouch, manual.
  8. `Shot 08 (Studio Luxury)`: High-contrast dramatic rim lighting highlighting sleek headphone contours against dark slate backdrop, luxury commercial look.
  9. `Shot 09 (Multi-Angle)`: Folded headphones view side-by-side with carrying case, showcasing compact portability.
  10. `Shot 10 (Promo Banner)`: Headphones on glowing red and gold holiday podium display banner backdrop, commercial festival vibes.
- **Post-Processing Command**:
  ```bash
  python skills/scenarios/crun-product-suite-generator/scripts/stitch_product_grid.py \
    shot_1.png shot_2.png shot_3.png shot_4.png shot_5.png shot_6.png shot_7.png shot_8.png shot_9.png shot_10.png \
    --title "Wireless ANC Headphones — Product Suite" \
    --grid 5x2 \
    -o headphones_suite_grid.png
  ```
