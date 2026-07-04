# SpinUpArt Custom Nodes for ComfyUI

Custom nodes for SpinUpArt workflows. Search **"spinupart"** in the ComfyUI
node picker to find every node in this pack — all display names start with
"SpinUpArt" and all nodes live under the `spinupart-utils` category.

## Nodes

### SpinUpArt String Template
Builds a single string from any number of string or numeric inputs.

- Connect any value (STRING, INT, FLOAT, ...) to the `INPUT0` slot; a new
  empty slot (`INPUT1`, `INPUT2`, ...) appears automatically after each
  connection. Disconnecting a slot removes it and renumbers the rest.
- Reference inputs in the template as `{{INPUT0}}`, `{{INPUT1}}`, etc.
- Numbers are converted to text (whole floats render without a trailing
  `.0`, so `3.0` becomes `3`).

Example template:

```
a portrait of {{INPUT0}} at {{INPUT1}} resolution, seed {{INPUT2}}
```

### SpinUpArt Syllable Counter
Counts the syllables in a string and outputs the total as an INT. Any text
inside parentheses (including nested ones) is ignored. Counting uses an
English vowel-group heuristic with adjustments for silent trailing `e`
("make"), consonant + `le` endings ("table"), and silent `ed` endings
("jumped").

### SpinUpArt Syllables to Frames
Converts a syllable count (e.g. from the Syllable Counter) into a total
frame count for a video clip:

```
frames = ceil((syllables / syllables_per_second + additional_time
               + groups * seconds_per_group) * frames_per_second)
```

Settings: `syllables_per_second` (speaking rate, default 5),
`additional_time` in seconds (default 3), `frames_per_second`
(default 25), and `seconds_per_group` (default 3). The result is rounded
up so the clip is never shorter than the spoken text needs.

The optional `grouped_text` string input adds `seconds_per_group` seconds
for every parenthesized group it contains — e.g.
`"he said (smiles) that we would see more (laughs)"` has two groups, adding
6 seconds at the default. Nested parentheses count as one group. When
`grouped_text` is not connected, no group time is added.

### SpinUpArt Webhook for Base64 image input
POSTs a base64 image payload to a webhook URL with an HMAC-SHA256 signature
(keyed by the `COMFYSIDE_KEY` environment variable). Returns the response
body and the post id.

### SpinUpArt Convert Image to Base64 string
Converts an IMAGE to a base64-encoded JPEG string with configurable quality.

### SpinUpArt Remove words from descriptions
Removes a space-separated list of words (case-insensitive, whole words) from
a description string and cleans up leftover whitespace.

## Adding a new node

1. Add the node class to `nodes.py` and register it in `NODE_CLASS_MAPPINGS`
   with a globally unique key.
2. Add a display name to `NODE_DISPLAY_NAME_MAPPINGS` — start it with
   "SpinUpArt" so it shows up in a "spinupart" search.
3. Set `CATEGORY = "spinupart-utils"` on the class.
4. If the node needs frontend behavior, add a `.js` file under `web/js/`
   (served via `WEB_DIRECTORY` in `__init__.py`).
5. Bump `version` in `pyproject.toml` before publishing to the registry.

## Installation

Clone into `ComfyUI/custom_nodes/` and restart ComfyUI:

```
cd ComfyUI/custom_nodes
git clone https://github.com/douglasgrim/comfy-spinupart
pip install -r comfy-spinupart/requirements.txt
```
