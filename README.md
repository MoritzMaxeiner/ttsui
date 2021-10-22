## Description

Minimal graphical application for accessing the Watson Text to Speech service.

## Requirements

- Python 3 plus all dependencies listed in `requirements.txt`.
- An IBM account with a Watson Text to Speech service instance.

## Usage

1. Set your Watson service url and api key in the settings file (e.g. `~/.config/ucw/ttsui.ini`).
2. Start the application with the python 3 interpreter (`$ python3 ttsui.py`).
3. Select language and voice.
4. Type some text to synthesize.
5. Press `Synthesize` to synthesize the text to speech, wait for `Play` to become ready.
6. Press `Play` to play the synthesized speech.

## Speech Data

All synthesized speech is stored in the persistent application directory (e.g. `~/.local/share/ucw/ttsui/speech`).

## License

This work is distributed under the terms of the GNU General Public License 3.0 or later.

`SPDX-License-Identifier: GPL-3.0-or-later`
