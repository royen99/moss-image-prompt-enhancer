# Evaluation

Manual checklist for the model built from the [Modelfile](../Modelfile). Run each input in [../examples/inputs.jsonl](../examples/inputs.jsonl) and score the output.

## Run

```powershell
ollama create moss-prompt-enhancer -f Modelfile
ollama run moss-prompt-enhancer "a woman reading in a cafe"
```

Run each input at least 3 times, because temperature is 0.7 and results vary.

## Checks for every output

| # | Check | Pass condition |
|---|-------|----------------|
| G1 | Output only | No preamble ("Here is..."), no explanation, no alternatives |
| G2 | No thinking blocks | No `<think>` text in output |
| G3 | No extras | No negative prompt, parameter list, or quality-tag list |
| G4 | Intent kept | Subject, medium, style, mood, and exclusions are preserved |
| G5 | Counts | Numbers of people and objects match the input |
| G6 | Language | English unless the input asks for another language |
| G7 | Length | Minimalist inputs stay short; complex inputs get more detail |

## Caption mode

| # | Check | Pass condition |
|---|-------|----------------|
| C1 | Plain text | No JSON, no Markdown fences, no coordinates |
| C2 | Cohesive | Reads as natural prose, not a checklist or labeled sections |
| C3 | Spatial words | Positions are described in words |
| C4 | Style respected | No photorealism or cinematic look added unless asked or implied |
| C5 | Quote handling | Quoted sentences are rendered as visible text only when intended |
| C6 | Visible text | Exact spelling, punctuation, capitalization, and line breaks; no invented slogans, logos, or watermarks |

## People

| # | Check | Pass condition |
|---|-------|----------------|
| P1 | Age present | Every human has an explicit age or range, even if the user gave none |
| P2 | Age respected | A user-supplied age is kept unchanged |
| P3 | Age inferred | Role or context changes the age (grandmother is elderly, student is about 20) |
| P4 | Ethnicity present | Every human has a stated ethnicity, even if the user gave none |
| P5 | Ethnicity respected | A user-supplied ethnicity is kept unchanged |
| P6 | Ethnicity inferred | Location or culture drives the choice (Seoul gives Korean, Dutch station gives Dutch) |
| P7 | Variation | With no indicators, repeated runs show different ethnicities (see below) |
| P8 | Non-humans | Robots, animals, and creatures get no age or ethnicity |
| P9 | Consistency | Appearance details match the stated age |

## Layout mode

| # | Check | Pass condition |
|---|-------|----------------|
| L1 | Valid JSON | Parses, with no fences and no surrounding text |
| L2 | Schema | Keys are `width`, `height`, `bbox_coord_space`, `bbox_format`, `summary`, `items`; no extra fields (`children`, `id`, `elements`) |
| L3 | Fixed values | `bbox_coord_space` is `"abs"`, `bbox_format` is `"xyxy"` |
| L4 | Labels | Each label is `object`, `character`, or `text` |
| L5 | Canvas | `summary.canvas` is `single`, `multi_panel`, or `collage` |
| L6 | Dimensions | Requested size is used; otherwise 1024x1024 or a size matching the ratio; sizes are not silently changed |
| L7 | Boxes | `[x_min, y_min, x_max, y_max]` in pixels from top-left, `x_min < x_max`, `y_min < y_max`, inside `0..width` and `0..height` |
| L8 | Text items | `text` field has exact wording, with `\n` for line breaks |
| L9 | Fit | Text box is large enough for its text length and line count |
| L10 | Real copy | No placeholders ("headline here"); no invented dates, prices, or addresses |
| L11 | Captions | Item captions describe appearance, not boxes or JSON |
| L12 | Compiles | The draft passes `compile_prompt.py` from the official MOSS-Image skill without errors |

## Mode selection

| Input | Expected mode |
|-------|---------------|
| Ordinary scenes, portraits, landscapes | caption |
| Explicit "caption mode" (even for a poster) | caption |
| Explicit "layout mode" | layout |
| Poster, infographic, multi-panel with specific placement | layout |

## Checking P7 (random ethnicity)

Run input `01-person-no-details` 10 times and tally the ethnicities. If more than half are the same, the "random" rule is not working well; consider listing explicit options in the Modelfile.

## Scoring

For each input record `pass`, `partial`, or `fail` per relevant check. Keep the results in a table:

| Input id | Run | G | C or L | P | Notes |
|----------|-----|---|--------|---|-------|
| 01-person-no-details | 1 | | | | |

Treat any failure of G1, G2, L1, L8, or P1/P4 on a person prompt as a regression to fix before publishing.
