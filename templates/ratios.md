Continue an existing cover set with your BUILT-IN image generation tool (imagegen / image_gen). Do NOT ask questions; work fully automatically. Do not draw anything with code/PIL — every cover must come from the built-in image generator. Skip brainstorming; the design is already approved.

## Approved 16:9 cover (the style + content master)
{{OUT}}/YouTube-16比9-高清.png
Main identity ref (ignore any burned-in captions): {{IDENTITY_MAIN}}

Keep EVERYTHING the same as the 16:9 master: same person and face ({{SUBJECT}}), same scene ({{SCENE}}), same filming setup ({{FILMING}}), same black diagonal rough brush panel with yellow splatter edges and the same lettering style, same small prop ({{PROP}}).
EYES: natural dark brown-black, clear lenses — absolutely NO green or teal eyes or lens tint.
LIKENESS: copy the real face and head proportions naturally from the identity refs — do not exaggerate, stretch, square off, widen or slim the face; the head stays in realistic proportion to the shoulders and the headwear. Clean, healthy skin (no heavy eye bags, dark circles or blotches), natural texture, not plastic.

Exact Chinese text ONLY, all four required, nothing else:
1. small yellow brush label with black text "{{LABEL}}"
2. bold white "{{LINE1}}"
3. bold white "{{LINE2}}"
4. BIGGEST vivid yellow "{{HEADLINE}}" — clearly bigger and heavier than the white lines in every ratio
Spell exactly: {{SPELL}}. Allowed line breaks: {{BREAKS}}.
Scene marks — the ONLY other writing allowed, each required, spelled exactly: {{SCENE_TEXTS}}.

Platform-compliance rules (posted on 抖音 and 小红书; violations get shadowbanned): NO logos, icons or names of YouTube / TikTok / Instagram or any platform (the Chinese scene marks above are allowed); NO money (no income numbers, no ¥ $ symbols, no banknotes); NO English, no QR codes, no account names, no watermarks, no UI; no other people.
{{EXTRA_RULES}}

Safe margins: all text, the label, the full head and glasses inside x=8%-92%, y=7%-93% — in practice keep letter strokes and the label inside x=12%-88%. Background may bleed to the edges; shoulders may exit the bottom; head never cropped; clear air above the head. Letters and props never cover the face or glasses. Every ratio is an independent RECOMPOSITION — never crop or stretch another version. Always pass the 16:9 master + identity ref as references.

## Ratios, in this priority order (do them one by one)
<<RATIO_LIST>>

After each generation, LOOK at the image. Regenerate (max 2 retries per ratio) if any Chinese character is wrong/missing/extra, any platform logo/name or money symbol appears, the eyes look green/teal, the face does not resemble the master, the head looks too big, a scene mark is wrong or missing, the filming setup changed, margins are violated, or the ratio is clearly wrong. Near-target sizes like 1448x1086 or 941x1672 are fine (do not retry for tiny ratio differences).

## Output
IMPORTANT: as soon as each ratio passes your check, IMMEDIATELY copy its PNG (original resolution, no resizing) to
{{OUT}}/<filename above>
before starting the next ratio (finished work survives if the run is cut off mid-way). If a ratio file already exists there, skip that ratio.
At the end write {{OUT}}/六比例-尺寸与完整提示词.md (output path, original pixel size and the exact final prompt for each ratio), and print each output path with its pixel size.
