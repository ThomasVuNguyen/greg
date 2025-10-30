# Goal

Build a data generation pipeline as follows

System prompt + object → three js → openscad replication → render → judge

We will use the Kimi model on CloudRift for code generation, use kimi.py

We use qwen3-vl for the VLM as a judge

# Milestone 0

Generate a set of 5 objects:

- A cat
- A house
- A ball
- A pen
- A pair of headphones

Status: Done

# Milestone 1

Achieve system prompt + object -> three js.

Deliverable:
- establish system prompt
- code extraction from the model is confirmed
- put the output in a file so i can review

Status: Done

# Milestone 2

Prompt the LLM to convert that three js code to openscad code

Deliverable:

- Openscad files

Status: Done
