# MOSS-Image Prompt Enhancer

An [Ollama](https://ollama.com) model that turns short image ideas into detailed prompts for the [MOSS-Image](https://github.com/OpenMOSS/MOSS-Image) text-to-image model.

It is based on the official [moss-image-prompt-enhancer skill](https://github.com/OpenMOSS/MOSS-Image/tree/main/skills/moss-image-prompt-enhancer), packaged as a local model so it can run offline without an agent.

## What it does

Give it a rough idea, get back only the enhanced prompt (no preamble, no explanations).

| Mode | Used for | Output |
|------|----------|--------|
| **Caption** (default) | Photos, portraits, landscapes, illustrations, paintings | One cohesive English prose description |
| **Layout** | Posters, infographics, multi-panel images, exact text placement | A JSON draft with pixel bounding boxes |

Behavior:

- **Keeps your intent:** subject, style, counts, exclusions, and exact visible text are preserved.
- **Avoids filler:** no quality-tag lists, no negative prompts, no invented slogans or watermarks. Minimalist requests stay minimalist.
- **People always get an age and an ethnicity.** If you give them, they are used exactly. If not, they are inferred from context (a Seoul night market gives Korean, "grandmother" gives elderly). With no clues the model picks one.
- **Honors an explicit mode** ("Layout mode, 1024x1536: ...", "Caption mode: ...") and an explicit canvas size.

See [examples/outputs.md](examples/outputs.md) for real outputs.

## Requirements

- [Ollama](https://ollama.com/download)
- Enough memory for the base model, `huihui_ai/qwen3-abliterated:8b` (about 5 GB download; roughly 8 GB of RAM or VRAM is comfortable)
- Python 3, only if you use Layout mode (see below)

## Install

```bash
git clone https://github.com/royen99/moss-image-prompt-enhancer
cd moss-image-prompt-enhancer
ollama create moss-prompt-enhancer -f Modelfile
```

The first run downloads the base model. Re-run the same command after editing the `Modelfile`; unchanged layers are reused.

## Usage

```bash
ollama run moss-prompt-enhancer "a woman reading in a cafe"
```

Or through the API:

```bash
curl http://127.0.0.1:11434/api/generate -d '{
  "model": "moss-prompt-enhancer",
  "prompt": "a street food vendor at a night market in Seoul",
  "stream": false
}'
```

Paste the result into MOSS-Image (for example in ComfyUI) as the positive prompt.

### Caption mode

Just describe the image:

```text
a grandmother knitting by a window, watercolor style
```

### Layout mode

Ask for it explicitly, or use a poster, infographic, or multi-panel idea. State the canvas size if you care about it:

```text
Layout mode, 1024x1536: a jazz concert poster. Title "SUMMER JAZZ NIGHT", below it "Friday 8 PM\nBlue Door Cafe". A saxophone player in the middle.
```

The model returns a **draft** with plain pixel boxes (`bbox_coord_space: "abs"`, `bbox_format: "xyxy"`, `[x_min, y_min, x_max, y_max]` from the top-left). MOSS-Image expects centered `yxyx` coordinates, so the draft must be compiled before use. The official skill ships the compiler:

```bash
python3 compile_prompt.py draft.json --output prompt.txt
```

Get `compile_prompt.py` from the [skill's `scripts` folder](https://github.com/OpenMOSS/MOSS-Image/tree/main/skills/moss-image-prompt-enhancer/scripts). It rejects invalid or out-of-bounds boxes. Use the width and height from the draft as the image size when generating. The compiled prompt itself does not contain the dimensions.

The model is not asked to do the coordinate arithmetic because small models get it wrong.

## Settings

Defined in the [Modelfile](Modelfile):

| Parameter | Value | Why |
|-----------|-------|-----|
| `temperature` | 0.7 | Some creative variety |
| `top_p` / `top_k` | 0.8 / 20 | Qwen3 recommended non-thinking sampling |
| `num_ctx` | 8192 | Fits the system prompt, examples, and output |
| `num_predict` | 2048 | Caps runaway output |

The `Modelfile` holds the full system prompt and a few example conversations (few-shot) that teach the layout format.

## Project layout

```text
Modelfile             system prompt, parameters, few-shot examples
examples/
  inputs.jsonl        20 test prompts with expected mode and focus checks
  outputs.md          real model outputs and known issues
  images/             optional generated images for the examples
tests/
  evaluation.md       manual checklist for scoring outputs
```

## Testing

Run each prompt from [examples/inputs.jsonl](examples/inputs.jsonl) against the model and score the result with [tests/evaluation.md](tests/evaluation.md). Because the model is sampled, run each prompt a few times.

## Known limitations

This runs on an 8B model, so rule-following is imperfect. Observed issues are listed in [examples/outputs.md](examples/outputs.md#known-issues). In short:

- Ethnicity is always stated, but "random" choices lean toward a few defaults.
- Characters in Layout mode are sometimes labeled `object` instead of `character`.
- A prompt like "write the prompt in Chinese: ..." can return unrelated text.
- The model occasionally invents visible text, such as a sign in a bar scene.
- Layout boxes are plausible but not always well composed. Check them before compiling.

A larger base model follows the rules more reliably. To try one, change the `FROM` line in the `Modelfile`.

## About the base model

The default base model, `huihui_ai/qwen3-abliterated:8b`, is a Qwen3 variant with its refusal behavior removed. That keeps it from refusing ordinary creative prompts, but it also means the model has **no built-in safety filtering**. The system prompt does not add content restrictions. Add your own if you plan to expose the model to other people.

If it prints `<think>` blocks, disable thinking (`ollama run --think=false moss-prompt-enhancer`, or `/set nothink` in a session).

## Credits

- Prompting guidance and Layout schema: [OpenMOSS/MOSS-Image](https://github.com/OpenMOSS/MOSS-Image), `skills/moss-image-prompt-enhancer`.
- Base model: [huihui_ai/qwen3-abliterated](https://ollama.com/huihui_ai/qwen3-abliterated), derived from [Qwen3](https://github.com/QwenLM/Qwen3).

This project is not affiliated with OpenMOSS or Alibaba. Check the licenses of the upstream projects above before redistributing.
