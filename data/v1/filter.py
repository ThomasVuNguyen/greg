#!/usr/bin/env python3
import json
import pathlib
import sys
import re


def get_project_root() -> pathlib.Path:
	return pathlib.Path(__file__).resolve().parents[2]


def get_data_dir() -> pathlib.Path:
	root = get_project_root()
	return root / "data" / "v1"


def get_animals_file() -> pathlib.Path:
	return get_data_dir() / "animals.json"


def get_output_file() -> pathlib.Path:
	out_dir = get_data_dir() / "out"
	out_dir.mkdir(parents=True, exist_ok=True)
	return out_dir / "animals_common.json"


CODE_BLOCK_RE = re.compile(
	r"```(?P<lang>[a-zA-Z0-9_-]*)\n(?P<code>[\s\S]*?)\n```",
	re.MULTILINE,
)


def extract_json_block(text: str) -> str:
	for m in CODE_BLOCK_RE.finditer(text):
		lang = (m.group("lang") or "").strip().lower()
		if lang in ("json", "json5"):
			return m.group("code").strip()
	return text.strip()


def read_animals() -> list:
	path = get_animals_file()
	if not path.exists():
		raise RuntimeError("animals.json not found.")
	text = path.read_text(encoding="utf-8").strip()
	if not text:
		raise RuntimeError("animals.json is empty.")
	data = json.loads(text)
	if not isinstance(data, list) or not all(isinstance(x, str) for x in data):
		raise RuntimeError("animals.json must be a JSON array of strings.")
	return data


def filter_common_animals(all_animals: list) -> list:
	# Ensure project root on sys.path to import inference.kimi
	project_root = str(get_project_root())
	if project_root not in sys.path:
		sys.path.insert(0, project_root)

	from inference.kimi import chat_with_kimi
	prompt = (
		"You are an expert curator. From the provided list of animal names, "
		"return ONLY the commonly known animals that an average person would recognize globally.\n"
		"- Return a pure JSON array of strings, no comments or explanations.\n"
		"- Do not add animals that are not in the input.\n\n"
		"Input list as JSON array follows:\n" + json.dumps(all_animals, ensure_ascii=False)
	)
	response = chat_with_kimi(prompt, stream=False)
	json_text = extract_json_block(response)
	parsed = json.loads(json_text)
	if not isinstance(parsed, list) or not all(isinstance(x, str) for x in parsed):
		raise RuntimeError("Model did not return a JSON array of strings.")
	# Intersect with input to guard against hallucinations
	allowed = set(all_animals)
	filtered = [name for name in parsed if name in allowed]
	return filtered


def main() -> None:
	animals = read_animals()
	common = filter_common_animals(animals)
	out_path = get_output_file()
	out_path.write_text(json.dumps(common, ensure_ascii=False, indent=2), encoding="utf-8")
	print(str(out_path))


if __name__ == "__main__":
	main()