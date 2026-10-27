You are making the 16:9 master of a Chinese video cover set with your BUILT-IN image generation tool (imagegen / image_gen). Do NOT ask questions; work fully automatically. Skip brainstorming. Do not draw anything with code/PIL — the cover must come from the built-in image generator.

## Style (black-and-yellow brush headline cover)
Black diagonal rough paint-brush panel behind the text with yellow splatter and spark edges; a small yellow brush-stroke label with black text at the top of the panel; two bold white rough brush Chinese lines; one HUGE vivid yellow rough brush headline with dark outline and glow (clearly bigger and heavier than the white lines, about 1.4x their letter height). Warm photoreal portrait of the person on the right, golden warm light, soft bokeh. Mobile-thumbnail readable.
STYLE refs (copy the graphic look, not their people or text):
{{STYLE_REFS}}

## Person
IDENTITY refs (photos of the person, also ATTACHED to this message — pass them to image_gen as reference images and match the face closely; ignore any burned-in captions):
{{IDENTITY_REFS}}
Subject: {{SUBJECT}}
Scene: {{SCENE}}
Filming / gear (follow exactly — do not substitute another device): {{FILMING}}
LIKENESS: copy the real face and head proportions naturally from the identity refs — do not exaggerate, stretch, square off, widen or slim the face; the head stays in realistic proportion to the shoulders and the headwear. Clean, healthy skin (no heavy eye bags, dark circles or blotches), natural texture, not plastic.
EYES: natural dark brown-black eyes; if wearing glasses, CLEAR lenses — absolutely NO green or teal eyes or lens tint.
Respectful and dignified: not sad, not pitiful, not caricatured, no exaggerated mouth.

## Text — exact Chinese text ONLY, all four required, nothing else
1. small yellow brush label with black text: "{{LABEL}}"
2. bold white rough brush line: "{{LINE1}}"
3. bold white rough brush line: "{{LINE2}}"
4. BIGGEST vivid yellow headline: "{{HEADLINE}}"
Spell exactly, character by character: {{SPELL}}. Arabic digits stay Arabic; full-width punctuation stays full-width.
Allowed line breaks: {{BREAKS}}.
Scene marks — the ONLY other writing allowed in the picture, each required, spelled exactly: {{SCENE_TEXTS}}.

## Platform-compliance rules (posted on 抖音 and 小红书; violations get the video shadowbanned)
- NO logos, icons or names of YouTube, TikTok, Instagram or any other platform anywhere (no red play-button icon, no app icons). The Chinese scene marks above are allowed.
- NO money: no income numbers, no ¥ $ or other currency symbols, no banknotes, no coins.
- NO English, no QR codes, no account names/handles, no watermarks, no UI screenshots, {{OTHER_PEOPLE}}.
- Secondary prop (small, never touching the text): {{PROP}}.
{{EXTRA_RULES}}

## Layout (16:9, ideally 1672x941 or 2048x1152)
Text block on the left ~58% on the black diagonal brush panel: label top-left, the two white lines, then the huge yellow headline. Person on the right ~42%, head fully inside with air above. Letters and props never cover the face or glasses.
Safe margins: all text, the label, the full head and glasses at least 8% from left/right edges and 7% from top/bottom. Background may bleed to the edges; shoulders may exit the bottom.

After generating, LOOK at the image. Regenerate (max 2 retries) if any Chinese character is wrong/missing/extra, any platform logo or money symbol appears, the eyes look green, the face does not resemble the identity refs or looks exaggerated, the head looks too big for the body, a scene mark is wrong or missing, the filming setup differs from the description, hands are malformed, or margins are violated. A size like 1672x941 is fine (do not retry for a 1-pixel ratio difference).

## Output
As soon as it passes, copy the PNG (original resolution, no resizing) to:
{{OUT}}/YouTube-16比9-高清.png
Finally print the output path with its pixel size, plus the exact prompt you used.
