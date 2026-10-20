You are revising the approved 16:9 master of a Chinese video cover set with your BUILT-IN image generation tool (imagegen / image_gen), in EDIT mode. Do NOT ask questions; work fully automatically. Skip brainstorming. Do not draw anything with code/PIL.

## Inputs
- BASE image to edit: {{BASE_IMAGE}}
- IDENTITY refs (keep the face faithful):
{{IDENTITY_REFS_EDIT}}

## The change
{{CHANGE}}

Keep EVERYTHING else identical to the base: same person and face, same eyes (natural dark brown-black, clear lenses, NO green tint), same scene, same black-and-yellow brush panel and lettering style. After the change the visible text must be exactly these four, nothing else:
1. "{{LABEL}}"  2. "{{LINE1}}"  3. "{{LINE2}}"  4. BIGGEST yellow "{{HEADLINE}}"
Spell exactly: {{SPELL}}.
Compliance: no platform logos/names (YouTube/TikTok/Instagram), no money symbols or income numbers, no English, no QR codes, no watermarks.
{{EXTRA_RULES}}

After generating, LOOK at the image. Regenerate (max 2 retries) if the change is not applied, any character is wrong, the face changed noticeably, the eyes look green, hands are malformed, or the text/head is closer than 8% to the left/right edges or 7% to the top/bottom. A size like 1672x941 is fine.

## Output
As soon as it passes, copy the PNG (original resolution, no resizing) to:
{{OUT}}/YouTube-16比9-高清.png
Finally print the output path with its pixel size, plus the exact prompt you used.
