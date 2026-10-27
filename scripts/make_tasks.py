"""Fill the prompt templates from a cover config and write the Codex task files.

usage: python3 make_tasks.py <cover.json>

Writes into config["work_dir"]:
  task-master.md   16:9 master (fresh generation, or EDIT when "base_image" is set)
  task-ratios.md   the other ratios, recomposed from the approved master
  ratios.txt       output-file stems run.sh waits for
  images-*.txt     reference images run.sh attaches (at most 5 per call)
See examples/cover.json for every field.
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent / "templates"
RATIO_STEMS = {
    "4:3": "抖音横版-4比3", "3:4": "视频号主页-3比4", "9:16": "竖屏封面-9比16",
    "1:1": "方图-1比1", "4:5": "Instagram-4比5", "21:9": "公众号-21比9",
}
DEFAULTS = {
    "label": "超叫兽 · 频道拆解",
    "prop": "a small smartphone lying on a surface near the text, whose screen shows ONLY a simple glowing "
            "yellow rising line/bar chart with an upward arrow — no logo, no words, no numbers",
    "ratios": list(RATIO_STEMS),
    "style_refs": [],
    "scene_texts": [],
    "extra_rules": "",
}
MAX_IMAGES = 5  # codex imagegen rejects more than 5 referenced images per call


def p(path):
    return str(Path(path).expanduser())


def bullets(paths, empty):
    return "\n".join(f"  - {p(x)}" for x in paths) if paths else f"  - {empty}"


def scene_texts(items):
    if not items:
        return "none (no other writing at all)"
    return "; ".join(f'"{x["text"]}" {x["where"]}' for x in items)


def other_people(desc, refs):
    if not desc:
        return "no other people"
    look = f" (appearance from these attached refs, NOT the identity refs: {', '.join(refs)})" if refs else ""
    return ("no other people except ONE small secondary figure: " + desc + look + " — the main person stays the clear focus: "
            "this figure is much smaller (at most about 1/8 of the frame height), placed in the background or on a screen, "
            "never in front of the main person and never competing with the text")


def capped(paths, what):
    if len(paths) > MAX_IMAGES:
        print(f"warning: {what} has {len(paths)} images, keeping the first {MAX_IMAGES} (codex limit)")
    return paths[:MAX_IMAGES]


def spell(s):
    return " ".join(ch for ch in s if not ch.isspace())


def main():
    cfg = {**DEFAULTS, **json.loads(Path(sys.argv[1]).expanduser().read_text())}
    work, out = Path(p(cfg["work_dir"])), Path(p(cfg["out_dir"]))
    work.mkdir(parents=True, exist_ok=True)
    t = cfg["texts"]
    ids = cfg.get("identity_refs", [])
    v = {
        "OUT": str(out),
        "LABEL": t.get("label", cfg["label"]), "LINE1": t["line1"], "LINE2": t["line2"], "HEADLINE": t["headline"],
        "STYLE_REFS": bullets(cfg["style_refs"], "none — follow the style description below exactly"),
        "IDENTITY_REFS": bullets(ids, "none — this is a fictional person; invent a natural, believable face"),
        "IDENTITY_REFS_EDIT": bullets(ids, "none — keep the face exactly as in the BASE image"),
        "IDENTITY_MAIN": p(ids[0]) if ids else "(none: fictional person — keep the master's face)",
        "SUBJECT": cfg["subject"], "SCENE": cfg["scene"], "FILMING": cfg["filming"], "PROP": cfg["prop"],
        "BREAKS": cfg.get("breaks", "none for the white lines; the yellow line may break at a natural point"),
        "SCENE_TEXTS": scene_texts(cfg["scene_texts"]),
        "OTHER_PEOPLE": other_people(cfg.get("secondary_person", ""), [p(x) for x in cfg.get("secondary_refs", [])]),
        "EXTRA_RULES": cfg["extra_rules"],
        "BASE_IMAGE": p(cfg.get("base_image", "")), "CHANGE": cfg.get("change", ""),
    }
    v["SPELL"] = " / ".join(spell(v[k]) for k in ("LINE1", "LINE2", "HEADLINE"))

    master_tpl = "edit-master.md" if cfg.get("base_image") else "master.md"
    for tpl, name in ((master_tpl, "task-master.md"), ("ratios.md", "task-ratios.md")):
        s = (HERE / tpl).read_text()
        for k, val in v.items():
            s = s.replace("{{" + k + "}}", val)
        if "{{" in s:
            sys.exit(f"unfilled placeholder in {tpl}: {s[s.index('{{'):s.index('{{') + 30]}")
        (work / name).write_text(s)

    ratios = [r for r in cfg["ratios"] if r in RATIO_STEMS]
    spec = (HERE / "ratio-specs.md").read_text().split("\n## ")
    keep = [blk for blk in spec[1:] if blk.split()[0] in ratios]
    body = "\n".join(f"{i}. " + blk.strip() for i, blk in enumerate(keep, 1))
    tr = (work / "task-ratios.md").read_text().replace("<<RATIO_LIST>>", body)
    (work / "task-ratios.md").write_text(tr)
    (work / "ratios.txt").write_text("\n".join(RATIO_STEMS[r] for r in ratios) + "\n")
    # run.sh attaches these with `codex exec --image`, so Codex sees the refs instead of only their paths
    # identity refs come first, so the cap drops style refs before faces
    sec = cfg.get("secondary_refs", []) if cfg.get("secondary_person") else []
    master_imgs = ([v["BASE_IMAGE"]] if cfg.get("base_image") else []) + [p(x) for x in ids + sec + cfg["style_refs"]]
    ratio_imgs = [f"{out}/YouTube-16比9-高清.png"] + [p(x) for x in ids + sec]
    (work / "images-master.txt").write_text("\n".join(capped(master_imgs, "master")) + "\n")
    (work / "images-ratios.txt").write_text("\n".join(capped(ratio_imgs, "ratios")) + "\n")
    print(f"wrote {work}/task-master.md ({master_tpl}), task-ratios.md, ratios.txt: {', '.join(ratios)}")


if __name__ == "__main__":
    main()
