#! /usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later

import sys
from pathlib import Path
from datetime import datetime

from PySide2.QtCore import (
	QCoreApplication,
	QSettings,
	QStandardPaths,
	QUrl
)

from PySide2.QtMultimedia import (
	QMediaPlayer
)

from PySide2.QtWidgets import (
	QApplication,
	QMainWindow,
	QWidget,
	QVBoxLayout,
	QHBoxLayout,
	QTextEdit,
	QComboBox,
	QPushButton,
)

from ibm_watson import TextToSpeechV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator


class WatsonTTS():
	def __init__(self, service_url, api_key):

		authenticator = IAMAuthenticator(api_key)

		self.service = TextToSpeechV1(authenticator=authenticator)

		self.service.set_service_url(service_url)

		voices = self.service.list_voices().get_result()["voices"]

		voices_per_language = {}
		for voice in voices:
			language = voice["language"]
			if not language in voices_per_language:
				voices_per_language[language] = []
			voices_per_language[language] += [(voice["name"], voice["description"])]
		self.voices_per_language = voices_per_language

		self.voice = None

	def set_voice(self, voice):
		self.voice = voice

	def __call__(self, text):
		 return self.service.synthesize(text, voice=self.voice, accept="audio/mp3").get_result().content


class TTSUI(QMainWindow):
	def __init__(self, settings, parent=None):
		super().__init__(parent)
		self.setWindowTitle("TTS UI")

		settings.beginGroup("Watson")
		self.synthesizer = WatsonTTS(settings.value("service_url"), settings.value("api_key"))
		settings.endGroup()

		self.speech_path = Path(QStandardPaths.writableLocation(QStandardPaths.AppDataLocation)) / "speech"
		self.speech_path.mkdir(parents=True, exist_ok=True)

		central_widget = QWidget()
		self.setCentralWidget(central_widget)

		central_layout = QVBoxLayout()
		central_widget.setLayout(central_layout)

		self.text_input = text_input = QTextEdit()
		central_layout.addWidget(text_input)

		self._filename = None
		text_input.textChanged.connect(self.invalidate_speech)

		bottom_layout = QHBoxLayout()
		central_layout.addLayout(bottom_layout)

		language_box = QComboBox()
		self.voice_box = voice_box = QComboBox()

		self.play_button = play_button = QPushButton()

		voice_box.currentIndexChanged.connect(self.select_voice)
		language_box.currentTextChanged.connect(self.select_language)

		for language in sorted(self.synthesizer.voices_per_language.keys()):
			language_box.addItem(language)

		bottom_layout.addWidget(language_box)
		bottom_layout.addWidget(voice_box)

		bottom_layout.insertStretch(2, 0)

		self.synthesize_button = synthesize_button = QPushButton()
		synthesize_button.setText("Synthesize")
		synthesize_button.clicked.connect(self.synthesize_text)
		bottom_layout.addWidget(synthesize_button)

		play_button.setText("Play")
		play_button.setEnabled(False)
		play_button.clicked.connect(self.play_speech)
		bottom_layout.addWidget(play_button)

		self.media_player = QMediaPlayer()


	def synthesize_text(self):
		text = self.text_input.toPlainText()

		if self._filename is None or not self._filename.exists():
			filename = datetime.now().strftime("%Y%m%dT%H%M%S")

			words = text.split(" ")
			if words[0]:
				filename +=  "__" + "_".join(words[:5])

			filename += ".mp3"

			self._filename = filename = (self.speech_path / filename).resolve()

			speech = self.synthesizer(text)
			with open(filename, "wb") as f:
				f.write(speech)
			self.play_button.setEnabled(True)

	def play_speech(self):
		self.media_player.setMedia(QUrl.fromLocalFile(str(self._filename)))
		self.media_player.setVolume(100)
		self.media_player.play()

	def invalidate_speech(self):
		self._filename = None
		self.play_button.setEnabled(False)

	def select_language(self, language):
		self.voice_box.clear()
		for name, description in self.synthesizer.voices_per_language[language]:
			self.voice_box.addItem(description, name)

	def select_voice(self, voice_index):
		self.synthesizer.set_voice(self.voice_box.itemData(voice_index))
		self.invalidate_speech()

if __name__ == "__main__":
	QCoreApplication.setOrganizationName("ucw")
	QCoreApplication.setApplicationName("ttsui")

	app = QApplication(sys.argv)

	settings = QSettings(QSettings.IniFormat, QSettings.UserScope, "ucw", "ttsui")

	settings.beginGroup("Watson")

	fail = False
	if not settings.contains("service_url") or settings.value("service_url") == "":
		settings.setValue("service_url", "")
		settings.sync()
		print(f"error: Set your service url for Watson Text to Speech in {settings.fileName()}", file=sys.stderr)
		fail = True
	if not settings.contains("api_key") or settings.value("api_key") == "":
		settings.setValue("api_key", "")
		settings.sync()
		print(f"error: Set your api key for Watson Text to Speech {settings.fileName()}", file=sys.stderr)
		fail = True
	settings.endGroup()

	if fail:
		raise RuntimeError("Settings incomplete")

	main_window = TTSUI(settings)

	main_window.show()

	raise SystemExit(app.exec_())
