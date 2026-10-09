#!/usr/bin/env python3
"""Genera data/index.json y data/threads.json a partir de data/editions/*.json.

index.json  -> lista ligera de las últimas ediciones (titulares) para la app.
threads.json -> temas en curso («Sigue la historia») con su etiqueta y última fecha.
Se ejecuta en cada despliegue de Netlify y también lo ejecuta la tarea diaria.
"""
import json, re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ED = ROOT / "data" / "editions"
MAX_INDEX = 60  # ediciones con titulares en el índice

def read_min(st):
    words = len((" ".join(st.get("body", [])) + " " + " ".join(st.get("keys", []))).split())
    return max(1, round(words / 200))

def main():
    files = sorted((p for p in ED.glob("*.json") if re.fullmatch(r"\d{4}-\d{2}-\d{2}\.json", p.name)), reverse=True)
    editions, threads = [], {}
    for i, p in enumerate(files):
        try:
            e = json.loads(p.read_text(encoding="utf-8"))
        except Exception as err:
            print(f"Saltando {p.name}: {err}")
            continue
        stories = e.get("stories", [])
        for st in stories:
            t = st.get("thread")
            if isinstance(t, dict) and t.get("id"):
                cur = threads.setdefault(t["id"], {"label": t.get("label", t["id"]), "last": e["date"], "first": e["date"], "count": 0})
                cur["count"] += 1
                cur["first"] = min(cur["first"], e["date"])
                if e["date"] >= cur["last"]:
                    cur["last"], cur["label"] = e["date"], t.get("label", cur["label"])
        if i < MAX_INDEX:
            editions.append({
                "date": e["date"],
                "number": e.get("number"),
                "summary": e.get("summary", ""),
                "briefsCount": len(e.get("briefs", [])),
                "hasWeekly": bool(e.get("weekly")),
                "essentials": e.get("essentials", [])[:6],
                "stories": [{
                    "id": st["id"], "section": st.get("section"), "weight": st.get("weight", 1),
                    "title": st.get("title", ""), "dek": st.get("dek", ""), "place": st.get("place", ""),
                    "figure": st.get("figure"), "thread": st.get("thread"), "min": read_min(st),
                    "sources": [{"name": s.get("name")} for s in st.get("sources", [])[:1]],
                } for st in stories],
            })
    out = ROOT / "data"
    (out / "index.json").write_text(json.dumps({"editions": editions}, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    ordered = dict(sorted(threads.items(), key=lambda kv: kv[1]["last"], reverse=True))
    (out / "threads.json").write_text(json.dumps(ordered, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"index.json: {len(editions)} ediciones · threads.json: {len(ordered)} temas")

if __name__ == "__main__":
    main()
