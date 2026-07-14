"""
cnfa_algs.validation.vlm_judge — send ordinary-language probes + images to a
vision LLM and collect ratings. Provider-agnostic; Gemini first (matches the
repo's GeminiMaterialAnalyzer convention: GEMINI_API_KEY or GOOGLE_API_KEY).

Usage (on a machine with a key):
    python -m cnfa_algs.validation.vlm_judge --images "example images/*.jpg" \
        --attrs cnfa.spatial.enclosure_index acoustic_absorption_proxy \
        --out judge_ratings.json --provider gemini --repeats 2

`--repeats N` re-asks each question N times (temperature>0) so you can run the
repo's variance-audit logic on the judge itself before trusting it.

Then: python -m cnfa_algs.validation.stats judge_ratings.json batch_scalar_matrix.csv
"""
from __future__ import annotations
import argparse, base64, glob, json, os, sys, time
from .probes import PROBES, ordinal_prompt, localization_prompt


def _b64(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()


def ask_gemini(prompt: str, image_paths: list, model="gemini-2.0-flash") -> str:
    import google.generativeai as genai
    genai.configure(api_key=os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY"))
    m = genai.GenerativeModel(model)
    parts = [prompt] + [{"mime_type": "image/jpeg", "data": _b64(p)} for p in image_paths]
    return m.generate_content(parts).text


def ask_anthropic(prompt: str, image_paths: list, model="claude-sonnet-4-5") -> str:
    import anthropic
    client = anthropic.Anthropic()
    content = []
    for p in image_paths:
        content.append({"type": "image", "source": {"type": "base64",
                        "media_type": "image/jpeg", "data": _b64(p)}})
    content.append({"type": "text", "text": prompt})
    r = client.messages.create(model=model, max_tokens=300,
                               messages=[{"role": "user", "content": content}])
    return r.content[0].text


PROVIDERS = {"gemini": ask_gemini, "anthropic": ask_anthropic}


def parse_json_loose(text: str):
    """Extract the first JSON object from a possibly chatty reply."""
    import re
    m = re.search(r"\{.*\}", text, re.S)
    if not m:
        return None
    try:
        return json.loads(m.group(0))
    except json.JSONDecodeError:
        return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--images", required=True)
    ap.add_argument("--attrs", nargs="+", default=list(PROBES.keys()))
    ap.add_argument("--out", default="judge_ratings.json")
    ap.add_argument("--provider", default="gemini", choices=list(PROVIDERS))
    ap.add_argument("--repeats", type=int, default=1)
    ap.add_argument("--localize", action="store_true")
    args = ap.parse_args()

    ask = PROVIDERS[args.provider]
    images = sorted(glob.glob(args.images))
    out = {"provider": args.provider, "repeats": args.repeats, "ratings": {}}
    for img in images:
        name = os.path.splitext(os.path.basename(img))[0]
        out["ratings"][name] = {}
        for key in args.attrs:
            entry = {"ordinal": [], "localization": []}
            for _ in range(args.repeats):
                try:
                    r = parse_json_loose(ask(ordinal_prompt(key), [img]))
                    if r:
                        entry["ordinal"].append(r)
                except Exception as e:
                    entry["ordinal"].append({"error": str(e)})
                time.sleep(0.6)
            if args.localize and PROBES[key]["localization"]:
                try:
                    r = parse_json_loose(ask(localization_prompt(key), [img]))
                    if r:
                        entry["localization"].append(r)
                except Exception as e:
                    entry["localization"].append({"error": str(e)})
            out["ratings"][name][key] = entry
            print(f"{name} :: {key} -> {entry['ordinal']}")
    with open(args.out, "w") as f:
        json.dump(out, f, indent=2)
    print("wrote", args.out)


if __name__ == "__main__":
    main()
