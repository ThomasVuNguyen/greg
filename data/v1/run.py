#!/usr/bin/env python3
import os
import json
import re
import pathlib
import datetime
import sys
from typing import List, Optional, Tuple

# Milestone 1: system prompt + object -> three js
# - establish system prompt
# - code extraction from the model is confirmed
# - put the output in a file so i can review


def get_project_root() -> pathlib.Path:
	return pathlib.Path(__file__).resolve().parents[2]


def get_output_dir() -> pathlib.Path:
	root = get_project_root()
	out_dir = root / "data" / "v1" / "out"
	out_dir.mkdir(parents=True, exist_ok=True)
	return out_dir


def get_objects() -> List[str]:
	return [
		"cat",
		"house",
		"ball",
		"pen",
		"headphones",
	]


def build_system_prompt() -> str:
	return (
		"You are an expert Three.js developer. Given a simple everyday object name, "
		"produce a single self-contained JavaScript snippet that uses Three.js to construct "
		"a minimal 3D scene approximating the object using basic primitives (BoxGeometry, "
		"SphereGeometry, CylinderGeometry, Torus, etc.). The output must be runnable in a "
		"vanilla HTML page with a <canvas>, include camera, lighting, renderer, animate loop, "
		"and add the object to the scene. Avoid external assets and textures. Do not include HTML; "
		"JavaScript only. Keep it concise and readable."
	)


def build_user_prompt(object_name: str) -> str:
	return (
		f"Object: {object_name}\n"
		"Task: Write JavaScript (no HTML) that sets up a Three.js scene and approximates the object.\n"
		"Constraints: Use only basic primitives. Include camera, lighting, renderer, controls optional.\n"
		"Return only JavaScript code, ideally fenced with ```javascript."
	)


def build_conversion_prompt(three_js_code: str) -> str:
	return (
		"Convert the following Three.js JavaScript snippet into equivalent OpenSCAD code.\n"
		"- Use OpenSCAD primitives (cube, sphere, cylinder, torus if needed), boolean ops, transforms.\n"
		"- Approximate materials/colors with comments; geometry fidelity is primary.\n"
		"- Do not return explanations. Return only OpenSCAD code fenced with ```openscad.\n\n"
		"```javascript\n" + three_js_code + "\n```"
	)

def request_model_completion(system_prompt: str, user_prompt: str) -> str:
	# Compose a single prompt because chat_with_kimi accepts a string prompt
	prompt = system_prompt + "\n\n" + user_prompt

	# Ensure project root is importable so `inference.kimi` can be resolved
	project_root = str(get_project_root())
	if project_root not in sys.path:
		sys.path.insert(0, project_root)

	# Lazy import to avoid top-level import issues when running from subdirectories
	from inference.kimi import chat_with_kimi
	try:
		return chat_with_kimi(prompt, stream=False)  # uses API key from inference/secret_key.py
	except Exception as e:
		raise RuntimeError(f"Model request failed: {e}")


CODE_BLOCK_RE = re.compile(
	# capture ```lang?\n...\n```
	r"```(?P<lang>[a-zA-Z0-9_-]*)\n(?P<code>[\s\S]*?)\n```",
	re.MULTILINE,
)


def extract_js_code_blocks(text: str) -> List[str]:
	blocks: List[str] = []
	for m in CODE_BLOCK_RE.finditer(text):
		lang = (m.group("lang") or "").strip().lower()
		code = m.group("code")
		if lang in ("js", "javascript", "typescript"):
			blocks.append(code)
	# If nothing fenced, heuristically accept the whole text if it looks like JS
	if not blocks and ("new THREE." in text or "import * as THREE" in text or "THREE.Scene(" in text):
		blocks.append(text.strip())
	return blocks


def extract_openscad_code_blocks(text: str) -> List[str]:
	blocks: List[str] = []
	for m in CODE_BLOCK_RE.finditer(text):
		lang = (m.group("lang") or "").strip().lower()
		code = m.group("code")
		if lang in ("openscad", "scad"):
			blocks.append(code)
	return blocks


def write_outputs(object_name: str, raw_text: str, code_blocks: List[str]) -> Tuple[pathlib.Path, List[pathlib.Path]]:
	out_root = get_output_dir() / object_name
	out_root.mkdir(parents=True, exist_ok=True)

	timestamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
	if not code_blocks:
		raise RuntimeError("No JavaScript code blocks detected; aborting with no output.")

	# Only write files when we have valid code blocks
	raw_path = out_root / f"response_{timestamp}.md"
	raw_path.write_text(raw_text, encoding="utf-8")

	written: List[pathlib.Path] = []
	for idx, code in enumerate(code_blocks, start=1):
		js_path = out_root / (f"three_{timestamp}.js" if len(code_blocks) == 1 else f"three_{timestamp}_{idx}.js")
		js_path.write_text(code, encoding="utf-8")
		written.append(js_path)
	return raw_path, written


def write_openscad_outputs(object_name: str, three_timestamp: str, raw_text: str, scad_blocks: List[str]) -> Tuple[pathlib.Path, List[pathlib.Path]]:
	out_root = get_output_dir() / object_name
	out_root.mkdir(parents=True, exist_ok=True)

	if not scad_blocks:
		raise RuntimeError("No OpenSCAD code blocks detected; aborting with no output.")

	raw_path = out_root / f"scad_response_{three_timestamp}.md"
	raw_path.write_text(raw_text, encoding="utf-8")

	written: List[pathlib.Path] = []
	for idx, code in enumerate(scad_blocks, start=1):
		scad_path = out_root / (f"model_{three_timestamp}.scad" if len(scad_blocks) == 1 else f"model_{three_timestamp}_{idx}.scad")
		scad_path.write_text(code, encoding="utf-8")
		written.append(scad_path)
	return raw_path, written


def main() -> None:
	objects = get_objects()
	system_prompt = build_system_prompt()

	for obj in objects:
		user_prompt = build_user_prompt(obj)
		response_text = request_model_completion(system_prompt, user_prompt)
		js_blocks = extract_js_code_blocks(response_text)
		# Write Three.js outputs
		raw_js_path, js_files = write_outputs(obj, response_text, js_blocks)
		# Use the same timestamp embedded in the js filename for pairing
		# three_<timestamp>[...].js -> extract <timestamp>
		first_js = js_files[0].name
		three_timestamp = first_js.split("_")[1].split(".")[0]

		# Convert each JS block to OpenSCAD
		for js_code in js_blocks:
			conv_prompt = build_conversion_prompt(js_code)
			scad_response = request_model_completion("You are an expert OpenSCAD engineer.", conv_prompt)
			scad_blocks = extract_openscad_code_blocks(scad_response)
			write_openscad_outputs(obj, three_timestamp, scad_response, scad_blocks)

	print(str(get_output_dir()))


if __name__ == "__main__":
	main()