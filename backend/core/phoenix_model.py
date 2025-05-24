"""
phoenix_model.py
----------------
Leichtgewichtiger Client für Leonardo AI – Phoenix-Modell.

✓  Kein UI-Code
✓  Vollständige Parametermenge laut offizieller Doku
✓  Saubere Typisierung & Validierung
✓  Keine externen Abhängigkeiten außer `requests`, `python-dotenv` (optional)
"""

from __future__ import annotations

import os
import time
import logging
import requests
from typing import List, Optional, Dict, Any

try:
    # .env-Support (optional)
    from dotenv import load_dotenv

    load_dotenv()
except ModuleNotFoundError:
    pass


# ------------------------------------------------------------------------------
# Konfiguration
# ------------------------------------------------------------------------------

LEONARDO_API_KEY: str | None = os.getenv("LEONARDO_API_KEY")

PHOENIX_MODEL_ID = "de7d3faf-762f-48e0-b3b7-9d0ac3a3fcf3"

#: Alle offiziell veröffentlichten Preset-Styles
PHOENIX_STYLES: dict[str, str] = {
    "3D Render": "debdf72a-91a4-467b-bf61-cc02bdeb69c6",
    "Bokeh": "9fdc5e8c-4d13-49b4-9ce6-5a74cbb19177",
    "Cinematic": "a5632c7c-ddbb-4e2f-ba34-8456ab3ac436",
    "Cinematic Concept": "33abbb99-03b9-4dd7-9761-ee98650b2c88",
    "Creative": "6fedbf1f-4a17-45ec-84fb-92fe524a29ef",
    "Dynamic": "111dc692-d470-4eec-b791-3475abac4c46",
    "Fashion": "594c4a08-a522-4e0e-b7ff-e4dac4b6b622",
    "Graphic Design Pop Art": "2e74ec31-f3a4-4825-b08b-2894f6d13941",
    "Graphic Design Vector": "1fbb6a68-9319-44d2-8d56-2957ca0ece6a",
    "HDR": "97c20e5c-1af6-4d42-b227-54d03d8f0727",
    "Illustration": "645e4195-f63d-4715-a3f2-3fb1e6eb8c70",
    "Macro": "30c1d34f-e3a9-479a-b56f-c018bbc9c02a",
    "Minimalist": "cadc8cd6-7838-4c99-b645-df76be8ba8d8",
    "Moody": "621e1c9a-6319-4bee-a12d-ae40659162fa",
    "None": "556c1ee5-ec38-42e8-955a-1e82dad0ffa1",
    "Portrait": "8e2bc543-6ee2-45f9-bcd9-594b6ce84dcd",
    "Pro B&W photography": "22a9a7d2-2166-4d86-80ff-22e2643adbcf",
    "Pro color photography": "7c3f932b-a572-47cb-9b9b-f20211e63b5b",
    "Pro film photography": "581ba6d6-5aac-4492-bebe-54c424a0d46e",
    "Portrait Fashion": "0d34f8e1-46d4-428f-8ddd-4b11811fa7c9",
    "Ray Traced": "b504f83c-3326-4947-82e1-7fe9e839ec0f",
    "Sketch (B&W)": "be8c6b58-739c-4d44-b9c1-b032ed308b61",
    "Sketch (Color)": "093accc3-7633-4ffd-82da-d34000dfc0d6",
    "Stock Photo": "5bdc3f2a-1be6-4d1c-8e77-992a30824a2c",
    "Vibrant": "dee282d3-891f-4f73-ba02-7f8131e5541b",
}

# Empfohlene Defaults aus der Doku
DEFAULTS: dict[str, Any] = dict(
    width=1472,
    height=832,
    num_images=4,
    contrast=3.5,
    alchemy=True,
    enhance_prompt=False,
    upscale=False,
    upscale_strength=0.35,
    style="Dynamic",
)

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("phoenix")


# ------------------------------------------------------------------------------
# Exceptions
# ------------------------------------------------------------------------------


class PhoenixError(RuntimeError):
    """Wrapper für alle Fehler innerhalb der Phoenix-Bibliothek."""


# ------------------------------------------------------------------------------
# Öffentliche API-Funktion
# ------------------------------------------------------------------------------


def generate_phoenix_images(
    *,
    prompt: str,
    num_images: int = DEFAULTS["num_images"],
    width: int = DEFAULTS["width"],
    height: int = DEFAULTS["height"],
    style: str = DEFAULTS["style"],
    contrast: float = DEFAULTS["contrast"],
    alchemy: bool = DEFAULTS["alchemy"],
    enhance_prompt: bool = DEFAULTS["enhance_prompt"],
    upscale: bool = DEFAULTS["upscale"],
    upscale_strength: float = DEFAULTS["upscale_strength"],
    negative_prompt: str | None = None,
    timeout: int = 30,
) -> List[bytes]:
    """
    Ruft Leonardo AI / Phoenix auf und gibt eine Liste roher Bild-Bytes zurück.

    Raises
    ------
    PhoenixError
        Bei fehlendem API-Key, HTTP-Fehlern oder unerwarteten Antworten.
    """
    if LEONARDO_API_KEY is None:
        raise PhoenixError("LEONARDO_API_KEY env variable not set")

    if style not in PHOENIX_STYLES:
        raise PhoenixError(f"Unknown style '{style}'. Valid keys: {', '.join(PHOENIX_STYLES)}")

    # ---------------- Request 1: Job anlegen ----------------
    url = "https://cloud.leonardo.ai/api/rest/v1/generations"
    headers = {
        "Authorization": f"Bearer {LEONARDO_API_KEY}",
        "Accept": "application/json",
        "Content-Type": "application/json",
    }

    payload: Dict[str, Any] = {
        "modelId": PHOENIX_MODEL_ID,
        "prompt": prompt[:1490],  # etwas Puffer zum 1500-Limit
        "num_images": num_images,
        "width": width,
        "height": height,
        "contrast": contrast,
        "styleUUID": PHOENIX_STYLES[style],
        "alchemy": alchemy,
        "enhancePrompt": enhance_prompt,
    }
    
    # Upscale parameters nur hinzufügen wenn upscale aktiviert ist
    if upscale:
        payload["upscale"] = upscale
        payload["upscaleStrength"] = upscale_strength
    if negative_prompt:
        payload["negative_prompt"] = negative_prompt

    resp = requests.post(url, headers=headers, json=payload, timeout=timeout)
    if resp.status_code != 200:
        raise PhoenixError(f"Leonardo API error {resp.status_code}: {resp.text}")

    try:
        generation_id = resp.json()["sdGenerationJob"]["generationId"]
    except (KeyError, TypeError):
        raise PhoenixError(f"Unexpected response: {resp.text}")

    # ---------------- Polling bis fertig --------------------
    status_url = f"https://cloud.leonardo.ai/api/rest/v1/generations/{generation_id}"
    t_start = time.time()
    while True:
        time.sleep(2.5)
        stat = requests.get(status_url, headers=headers, timeout=timeout).json().get("generations_by_pk", {})
        status = stat.get("status", "PENDING")
        if status in {"COMPLETE", "FAILED"}:
            break
        # Einfaches Timeout-Handling
        if time.time() - t_start > 300:
            raise PhoenixError("Polling timeout after 5 min")

    if status != "COMPLETE":
        raise PhoenixError(f"Generation failed: {status}")

    log.info("Phoenix generation finished – downloading images …")

    # ---------------- Bilder herunterladen ------------------
    image_bytes: List[bytes] = []
    img_urls = [img["url"] for img in stat.get("generated_images", [])]
    for url in img_urls:
        img_resp = requests.get(url, timeout=timeout)
        if img_resp.status_code == 200:
            image_bytes.append(img_resp.content)
        else:
            log.warning("Could not download %s (HTTP %s)", url, img_resp.status_code)

    return image_bytes


# ------------------------------------------------------------------------------
# Mini-CLI / Quick Test
# ------------------------------------------------------------------------------

if __name__ == "__main__":
    import argparse, pathlib, base64, textwrap

    parser = argparse.ArgumentParser(
        description="Quick CLI test for Leonardo-Phoenix model",
        formatter_class=argparse.RawTextHelpFormatter,
        epilog=textwrap.dedent(
            """
            Beispiele:
              python phoenix_model.py -p "majestic dragon" -n 2 -s Cinematic
              python phoenix_model.py -p "portrait woman" --width 832 --height 1472 -s Portrait
              python phoenix_model.py -p "landscape" --contrast 5.0 --no-alchemy
              python phoenix_model.py -p "futuristic city" --negative "old, vintage" --enhance
            """
        ),
    )
    parser.add_argument("-p", "--prompt", required=True, help="Text prompt")
    parser.add_argument("-n", "--num_images", type=int, default=2, help="How many images")
    parser.add_argument("-s", "--style", default="Dynamic", choices=list(PHOENIX_STYLES), help="Art style")
    parser.add_argument("--outdir", default="phoenix_out", help="Output folder")
    
    # Erweiterte Parameter
    parser.add_argument("--width", type=int, default=DEFAULTS["width"], help="Image width")
    parser.add_argument("--height", type=int, default=DEFAULTS["height"], help="Image height")
    parser.add_argument("--contrast", type=float, default=DEFAULTS["contrast"], help="Contrast level (1.0-5.0)")
    parser.add_argument("--no-alchemy", action="store_true", help="Disable Alchemy mode")
    parser.add_argument("--enhance", action="store_true", help="Enable prompt enhancement")
    parser.add_argument("--negative", type=str, help="Negative prompt")
    parser.add_argument("--upscale", action="store_true", help="Enable upscaling")
    parser.add_argument("--upscale-strength", type=float, default=DEFAULTS["upscale_strength"], help="Upscale strength")

    args = parser.parse_args()

    imgs = generate_phoenix_images(
        prompt=args.prompt,
        num_images=args.num_images,
        style=args.style,
        width=args.width,
        height=args.height,
        contrast=args.contrast,
        alchemy=not args.no_alchemy,
        enhance_prompt=args.enhance,
        negative_prompt=args.negative,
        upscale=args.upscale,
        upscale_strength=args.upscale_strength,
    )

    outdir = pathlib.Path(args.outdir)
    outdir.mkdir(exist_ok=True)
    for idx, data in enumerate(imgs, 1):
        fname = outdir / f"phoenix_{idx}.png"
        fname.write_bytes(data)
        print("✔ saved", fname)