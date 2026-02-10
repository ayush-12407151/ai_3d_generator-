import os
import sys

# ---------------- GEOMETRY FAMILY ----------------
def detect_geometry_family(text):
    t = text.lower()

    if "toothbrush" in t or "tooth brush" in t:
        return "container"
    if any(w in t for w in ["container", "box", "cup", "storage"]):
        return "container"
    if any(w in t for w in ["hook", "hang"]):
        return "hook"
    if any(w in t for w in ["stand", "support", "upright", "hold "]):
        return "stand"

    return "container"


# ---------------- PARAMETER INFERENCE ----------------
def infer_parameters(family, text):
    t = text.lower()

    p = {
        "height": 120,
        "width": 80,
        "depth": 80,
        "angle": 60,
        "wall": 4,
        "slots": 0,
        "drain": 0,
        "load": "normal"
    }

    # load-aware intent
    if any(w in t for w in ["strong", "heavy", "load"]):
        p["load"] = "high"
        p["wall"] += 2
        p["width"] += 10

    if "tablet" in t:
        p["width"] = 120

    if "bed" in t:
        p["angle"] = 70

    if "desk" in t:
        p["angle"] = 50

    # toothbrush specialization
    if "toothbrush" in t or "tooth brush" in t:
        p.update({
            "height": 120,
            "width": 60,
            "depth": 60,
            "wall": 3,
            "slots": 3,
            "drain": 1
        })
        for n in ["2", "3", "4", "5"]:
            if n in t:
                p["slots"] = int(n)

    return p


# ---------------- AUTO-CORRECTION (TIER-1) ----------------
def auto_correct_design(family, p):
    corrections = []

    if family == "stand" and p["angle"] > 65:
        old = p["angle"]
        p["angle"] = 60
        corrections.append(f"Angle auto-reduced {old}° → 60°")

    if p["wall"] < 2:
        old = p["wall"]
        p["wall"] = 2
        corrections.append(f"Wall increased {old} → 2 mm")

    ratio = p["height"] / max(p["width"], 1)
    if ratio > 1.8:
        old = p["width"]
        p["width"] += 20
        corrections.append(f"Width increased {old} → {p['width']} mm for stability")

    return p, corrections


# ---------------- MANUFACTURABILITY DECISION ----------------
def manufacturability_decision(family, p):
    approved = True
    reasons = []

    if family == "stand" and p["angle"] > 65:
        approved = False
        reasons.append("Overhang angle too steep")

    if p["wall"] < 1.2:
        approved = False
        reasons.append("Wall too thin for FDM printing")

    if p["height"] / max(p["width"], 1) > 2.0:
        approved = False
        reasons.append("Tall & narrow geometry unstable")

    if approved:
        reasons.append("Self-supporting geometry, no supports required")

    return approved, reasons


# ---------------- STRENGTH SCORE ----------------
def strength_score(family, p):
    score = 100

    if p["wall"] < 2:
        score -= 20

    if p["load"] == "high":
        score -= 5  # conservative adjustment

    ratio = p["height"] / max(p["width"], 1)
    if ratio > 1.8:
        score -= 30
    elif ratio > 1.5:
        score -= 15

    if family == "stand" and p["angle"] > 65:
        score -= 15

    score = max(0, min(100, score))

    label = (
        "Excellent" if score >= 85 else
        "Good" if score >= 70 else
        "Fair" if score >= 50 else
        "Weak"
    )

    return score, label


# ---------------- SCAD + STL ----------------
def generate_scad(template_path, params):
    with open(template_path) as f:
        scad = f.read()

    for k, v in params.items():
        scad = scad.replace(f"{k} = 0;", f"{k} = {v};")

    with open("temp.scad", "w") as f:
        f.write(scad)


def export_stl():
    os.system("openscad -o output/model.stl temp.scad")


# ---------------- MAIN ----------------
def main(text):
    family = detect_geometry_family(text)
    params = infer_parameters(family, text)
    params, corrections = auto_correct_design(family, params)
    approved, reasons = manufacturability_decision(family, params)
    score, label = strength_score(family, params)

    with open("output/decision.txt", "w") as f:
        f.write(f"FAMILY={family}\n")
        f.write(f"APPROVED={approved}\n")
        f.write(f"PARAMS={params}\n")
        f.write(f"CORRECTIONS={'; '.join(corrections)}\n")
        f.write(f"REASONS={'; '.join(reasons)}\n")
        f.write(f"STRENGTH_SCORE={score}\n")
        f.write(f"STRENGTH_LABEL={label}\n")

    if approved:
        generate_scad(f"families/{family}.scad", params)
        export_stl()


if __name__ == "__main__":
    main(sys.argv[1])
