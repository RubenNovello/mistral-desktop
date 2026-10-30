#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Mistral Desktop — client desktop non ufficiale per Mistral AI
================================================================
- Motore: Ollama locale (gratis, privacy, offline) OPPURE API Mistral (cloud)
- UI: PySide6 (Qt 6), tema scuro in stile Mistral
- Core Rust opzionale: se il modulo `mistral_desktop_core` è installato,
  lo streaming passa al core Rust (PyO3) per le massime prestazioni.
- Chat salvate in ~/.local/share/mistral-desktop/chats/

AVVIO RAPIDO:
    python3 -m venv .venv && source .venv/bin/activate
    pip install PySide6 requests
    python mistral_desktop.py

 Questo progetto NON è affiliato a Mistral AI. Uso del marchio a solo
scopo identificativo del client. Licenza MIT.
"""

import html as html_mod
import json
import os
import sys
from datetime import datetime
from pathlib import Path

import requests
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QApplication, QComboBox, QDialog, QDoubleSpinBox, QFormLayout,
    QHBoxLayout, QLabel, QLineEdit, QListWidget, QListWidgetItem,
    QMainWindow, QMessageBox, QPushButton, QStackedWidget, QTextBrowser,
    QTextEdit, QVBoxLayout, QWidget,
)

APP_NAME = "Mistral Desktop"
APP_VERSION = "0.1.0"
ORG = "mistral-desktop-community"

CONFIG_DIR = Path.home() / ".config" / "mistral-desktop"
DATA_DIR = Path.home() / ".local" / "share" / "mistral-desktop"
CHATS_DIR = DATA_DIR / "chats"
CONFIG_PATH = CONFIG_DIR / "settings.json"

MISTRAL_API_BASE = "https://api.mistral.ai/v1"

DEFAULT_SETTINGS = {
    "engine": "ollama",                      # "ollama" | "mistral"
    "ollama_host": "http://localhost:11434",
    "mistral_api_key": "",
    "model_ollama": "devstral-small-2:24b",
    "model_mistral": "mistral-medium-latest",
    "temperature": 0.2,
    "system_prompt": "Rispondi in italiano, in modo conciso e preciso.",
}

# ------------------------------------------------------------------ core Rust

try:
    import mistral_desktop_core as _rust_core  # opzionale, buildato con maturin
    HAS_RUST_CORE = True
except ImportError:
    _rust_core = None
    HAS_RUST_CORE = False


# ------------------------------------------------------------------ settings

def load_settings() -> dict:
    try:
        return {**DEFAULT_SETTINGS, **json.loads(CONFIG_PATH.read_text())}
    except Exception:
        return dict(DEFAULT_SETTINGS)


def save_settings(settings: dict) -> None:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    CONFIG_PATH.write_text(json.dumps(settings, indent=2))


# --------------------------------------------------------------- motori chat

def list_ollama_models(host: str):
    r = requests.get(f"{host}/api/tags", timeout=5)
    r.raise_for_status()
    return sorted(m["name"] for m in r.json().get("models", []))


def list_mistral_models(api_key: str):
    r = requests.get(f"{MISTRAL_API_BASE}/models",
                     headers={"Authorization": f"Bearer {api_key}"}, timeout=10)
    r.raise_for_status()
    return sorted(m["id"] for m in r.json().get("data", []))


def stream_ollama(host, model, messages, temperature, on_chunk, should_stop):
    payload = {"model": model, "messages": messages, "stream": True,
               "options": {"temperature": temperature}}
    with requests.post(f"{host}/api/chat", json=payload, stream=True,
                       timeout=600) as r:
        r.raise_for_status()
        for line in r.iter_lines():
            if should_stop():
                break
            if not line:
                continue
            data = json.loads(line)
            if data.get("done"):
                break
            piece = data.get("message", {}).get("content", "")
            if piece:
                on_chunk(piece)


def stream_mistral(api_key, model, messages, temperature, on_chunk, should_stop):
    payload = {"model": model, "messages": messages, "stream": True,
               "temperature": temperature}
    headers = {"Authorization": f"Bearer {api_key}",
               "Content-Type": "application/json"}
    with requests.post(f"{MISTRAL_API_BASE}/chat/completions", json=payload,
                       headers=headers, stream=True, timeout=600) as r:
        r.raise_for_status()
        for raw in r.iter_lines():
            if should_stop():
                break
            if not raw or not raw.startswith(b"data:"):
                continue
            chunk = raw[5:].strip()
            if chunk == b"[DONE]":
                break
            delta = json.loads(chunk)["choices"][0]["delta"].get("content", "")
            if delta:
                on_chunk(delta)


class ChatWorker(QThread):
    chunk = Signal(str)
    finished_ok = Signal()
    failed = Signal(str)

    def __init__(self, settings, messages, parent=None):
        super().__init__(parent)
        self.settings = settings
        self.messages = messages
        self._stop = False

    def stop(self):
        self._stop = True

    def _on_chunk(self, piece: str):
        if not self._stop:
            self.chunk.emit(piece)

    def run(self):
        s = self.settings
        try:
            if s["engine"] == "ollama":
                if HAS_RUST_CORE and hasattr(_rust_core, "ollama_stream"):
                    _rust_core.ollama_stream(
                        s["ollama_host"], s["model_ollama"], self.messages,
                        s["temperature"], self._on_chunk)
                else:
                    stream_ollama(s["ollama_host"], s["model_ollama"],
                                  self.messages, s["temperature"],
                                  self._on_chunk, lambda: self._stop)
            else:
                if HAS_RUST_CORE and hasattr(_rust_core, "mistral_stream"):
                    _rust_core.mistral_stream(
                        s["mistral_api_key"], s["model_mistral"],
                        self.messages, s["temperature"], self._on_chunk)
                else:
                    stream_mistral(s["mistral_api_key"], s["model_mistral"],
                                   self.messages, s["temperature"],
                                   self._on_chunk, lambda: self._stop)
            self.finished_ok.emit()
        except requests.exceptions.ConnectionError:
            self.failed.emit("Connessione non riuscita. "
                             "Ollama è in esecuzione? Prova: ollama serve")
        except requests.exceptions.HTTPError as e:
            self.failed.emit(f"Errore dal server: {e}")
        except Exception as e:  # noqa: BLE001
            self.failed.emit(str(e))


# ------------------------------------------------------------------ utilità UI

ACCENT = "#ff8205"
BG = "#0f1017"
SIDEBAR = "#15161f"
CARD = "#1c1d29"
FG = "#e6e6ec"
MUTED = "#8b8d9a"


def md_to_html(text: str) -> str:
    """Mini-markdown: blocchi ```codice``` e testo semplice."""
    import html as _h
    import re as _re
    parts = _re.split("```", text)
    out = []
    for i, part in enumerate(parts):
        if i % 2 == 1:
            code = _re.sub(r"^[a-zA-Z0-9_-]*\n", "", part)
            out.append(
                "<pre style='background:#101018;border:1px solid #2a2b3a;"
                "border-radius:8px;padding:10px;color:#ffd9a8;"
                f"white-space:pre-wrap'>{_h.escape(code)}</pre>")
        elif part.strip():
            out.append(
                f"<p style='white-space:pre-wrap'>{_h.escape(part)}</p>")
    return "".join(out) or "<p>…</p>"


def chat_html(messages, model_label):
    rows = []
    for m in messages:
        if m["role"] == "user":
            rows.append(
                f"<div style='text-align:right;margin:14px 0'>"
                f"<span style='display:inline-block;background:{ACCENT};"
                f"color:#14151f;border-radius:14px 14px 3px 14px;"
                f"padding:8px 14px;text-align:left'>{html_mod.escape(m['content'])}</span></div>")
        else:
            rows.append(
                f"<div style='margin:14px 0'><div style='color:{MUTED};"
                "font-size:11px;margin-bottom:3px'>"
                f"{html_mod.escape(m.get('model', model_label))}</div>"
                f"<div style='background:{CARD};border:1px solid #26273a;"
                "border-radius:12px;padding:12px 14px'>"
                f"{md_to_html(m['content'])}</div></div>")
    return "".join(rows)


# ------------------------------------------------------------------- finestre

class SettingsDialog(QDialog):
    def __init__(self, settings, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Impostazioni — Mistral Desktop")
        self.setMinimumWidth(460)
        self.settings = dict(settings)
        lay = QFormLayout(self)

        self.engine = QComboBox()
        self.engine.addItem("🦙  Ollama locale", "ollama")
        self.engine.addItem("☁️  API Mistral", "mistral")
        self.engine.setCurrentIndex(0 if settings["engine"] == "ollama" else 1)
        lay.addRow("Motore predefinito:", self.engine)

        self.host = QLineEdit(settings["ollama_host"])
        lay.addRow("Host Ollama:", self.host)

        self.api_key = QLineEdit(settings["mistral_api_key"])
        self.api_key.setEchoMode(QLineEdit.Password)
        lay.addRow("API key Mistral:", self.api_key)

        self.temp = QDoubleSpinBox()
        self.temp.setRange(0.0, 1.0)
        self.temp.setSingleStep(0.1)
        self.temp.setValue(settings["temperature"])
        lay.addRow("Temperatura:", self.temp)

        self.system_prompt = QLineEdit(settings.get("system_prompt", ""))
        lay.addRow("System prompt:", self.system_prompt)

        btns = QHBoxLayout()
        ok = QPushButton("Salva")
        ok.clicked.connect(self.accept)
        cancel = QPushButton("Annulla")
        cancel.clicked.connect(self.reject)
        btns.addStretch(1)
        btns.addWidget(cancel)
        btns.addWidget(ok)
        lay.addRow(btns)

    def values(self):
        s = dict(self.settings)
        s.update(engine=self.engine.currentData(),
                 ollama_host=self.host.text().strip() or DEFAULT_SETTINGS["ollama_host"],
                 mistral_api_key=self.api_key.text().strip(),
                 temperature=self.temp.value(),
                 system_prompt=self.system_prompt.text())
        return s


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.settings = load_settings()
        self.chats = self._load_chats()
        self.current_chat = None
        self.worker = None

        self.setWindowTitle(f"{APP_NAME} — client non ufficiale · v{APP_VERSION}")
        self.resize(1200, 760)

        root = QHBoxLayout()
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ---------------- sidebar
        side = QVBoxLayout()
        side.setContentsMargins(12, 14, 12, 12)
        side.setSpacing(8)

        brand = QHBoxLayout()
        logo = QLabel("✦")
        logo.setStyleSheet(f"color:{ACCENT};font-size:22px;font-weight:800")
        title = QLabel(APP_NAME)
        title.setStyleSheet(f"color:{FG};font-size:15px;font-weight:700")
        brand.addWidget(logo)
        brand.addWidget(title)
        brand.addStretch(1)
        side.addLayout(brand)

        new_chat = QPushButton("＋  Nuova chat")
        new_chat.setCursor(Qt.PointingHandCursor)
        new_chat.setStyleSheet(
            f"background:qlineargradient(x1:0,y1:0,x2:1,y2:0,stop:0 {ACCENT},stop:1 #ffb347);"
            "color:#14151f;font-weight:700;border:none;border-radius:10px;padding:10px")
        new_chat.clicked.connect(self.new_chat)
        side.addWidget(new_chat)

        self.chat_list = QListWidget()
        self.chat_list.setFixedWidth(252)
        self.chat_list.setStyleSheet(f"background:{SIDEBAR};border:none;color:{FG}")
        self.chat_list.itemClicked.connect(self._open_chat)
        side.addWidget(self.chat_list, 1)

        self.engine_combo = QComboBox()
        self.engine_combo.setCursor(Qt.PointingHandCursor)
        self.engine_combo.addItem("🦙 Ollama locale", "ollama")
        self.engine_combo.addItem("☁️ API Mistral", "mistral")
        self.engine_combo.setCurrentIndex(0 if self.settings["engine"] == "ollama" else 1)
        self.engine_combo.currentIndexChanged.connect(self._engine_changed)
        self.engine_combo.setStyleSheet(
            f"background:{CARD};color:{FG};border:1px solid #26273a;"
            "border-radius:10px;padding:8px")
        side.addWidget(self.engine_combo)

        self.model_combo = QComboBox()
        self.model_combo.setCursor(Qt.PointingHandCursor)
        self.model_combo.setStyleSheet(
            f"background:{CARD};color:{FG};border:1px solid #26273a;"
            "border-radius:10px;padding:8px")
        side.addWidget(self.model_combo)

        refresh = QPushButton("⟳  Aggiorna modelli")
        refresh.setCursor(Qt.PointingHandCursor)
        refresh.setStyleSheet(f"background:transparent;color:{MUTED};border:none;padding:4px")
        refresh.clicked.connect(self.refresh_models)
        side.addWidget(refresh)

        settings_btn = QPushButton("⚙  Impostazioni")
        settings_btn.setCursor(Qt.PointingHandCursor)
        settings_btn.setStyleSheet(f"background:transparent;color:{MUTED};border:none;padding:4px")
        settings_btn.clicked.connect(self.open_settings)
        side.addWidget(settings_btn)

        self.status = QLabel("…")
        self.status.setStyleSheet(f"color:{MUTED};font-size:11px")
        side.addWidget(self.status)

        sidebar = QWidget()
        sidebar.setLayout(side)
        sidebar.setStyleSheet(f"background:{SIDEBAR}")
        root.addWidget(sidebar)

        # ---------------- area principale
        self.stack = QStackedWidget()

        welcome = QWidget()
        wlay = QVBoxLayout(welcome)
        wlay.setAlignment(Qt.AlignCenter)
        user = os.environ.get("USER") or "tu"
        hour = datetime.now().hour
        greet = "Buongiorno" if hour < 13 else ("Buon pomeriggio" if hour < 18 else "Buonasera")
        big = QLabel(f"👋 {greet}, {user}!")
        big.setAlignment(Qt.AlignCenter)
        big.setStyleSheet(f"color:{FG};font-size:34px;font-weight:800")
        sub = QLabel("Come posso aiutarti oggi?")
        sub.setAlignment(Qt.AlignCenter)
        sub.setStyleSheet(f"color:{MUTED};font-size:15px")
        wlay.addSpacing(120)
        wlay.addWidget(big)
        wlay.addWidget(sub)

        chips = QHBoxLayout()
        chips.setSpacing(10)
        for label in ("🐍 Script Python", "🐛 Debug errore", "✅ Unit test", "🔧 Refactoring"):
            b = QPushButton(label)
            b.setCursor(Qt.PointingHandCursor)
            b.setStyleSheet(
                f"background:{CARD};color:{FG};border:1px solid #26273a;"
                "border-radius:12px;padding:12px 16px")
            b.clicked.connect(lambda _, t=label: self.quick_send(t))
            chips.addWidget(b)
        wlay.addSpacing(24)
        wlay.addLayout(chips)
        wlay.addStretch(1)
        self.stack.addWidget(welcome)

        chat_page = QWidget()
        clay = QVBoxLayout(chat_page)
        clay.setContentsMargins(0, 0, 0, 0)
        self.view = QTextBrowser()
        self.view.setStyleSheet(
            f"background:{BG};color:{FG};border:none;padding:18px")
        self.view.setOpenExternalLinks(True)
        clay.addWidget(self.view)

        input_bar = QHBoxLayout()
        input_bar.setContentsMargins(18, 8, 18, 14)
        self.input = QTextEdit()
        self.input.setPlaceholderText("Scrivi un messaggio… (Invio per inviare, Shift+Invio per andare a capo)")
        self.input.setFixedHeight(64)
        self.input.setStyleSheet(
            f"background:{CARD};color:{FG};border:1px solid #26273a;"
            "border-radius:14px;padding:12px")
        self.input.installEventFilter(self)
        input_bar.addWidget(self.input, 1)

        self.send_btn = QPushButton("Invia ▲")
        self.send_btn.setCursor(Qt.PointingHandCursor)
        self.send_btn.setFixedHeight(64)
        self.send_btn.setStyleSheet(
            f"background:qlineargradient(x1:0,y1:0,x2:1,y2:0,stop:0 {ACCENT},stop:1 #ffb347);"
            "color:#14151f;font-weight:700;border:none;border-radius:14px;padding:0 22px")
        self.send_btn.clicked.connect(self._on_send)
        input_bar.addWidget(self.send_btn)
        clay.addLayout(input_bar)
        self.stack.addWidget(chat_page)

        root.addWidget(self.stack, 1)
        central = QWidget()
        central.setLayout(root)
        self.setCentralWidget(central)
        self.setStyleSheet(f"QMainWindow{{background:{BG}}}")

        self._refresh_chat_list()
        self._engine_changed()
        self.status.setText(
            ("core: Rust (PyO3) ⚡" if HAS_RUST_CORE else "core: Python") +
            f" · {len(self.chats)} chat salvate")

    # ------------------------------------------------------------ chat store

    def _load_chats(self):
        CHATS_DIR.mkdir(parents=True, exist_ok=True)
        chats = []
        for f in sorted(CHATS_DIR.glob("*.json"), key=os.path.getmtime,
                        reverse=True):
            try:
                chats.append(json.loads(f.read_text()))
            except Exception:
                continue
        return chats

    def _refresh_chat_list(self):
        self.chat_list.clear()
        for c in self.chats:
            it = QListWidgetItem(c.get("title", "Chat"))
            it.setData(Qt.UserRole, c["id"])
            self.chat_list.addItem(it)

    def _chat_path(self, chat_id):
        return CHATS_DIR / f"{chat_id}.json"

    def _save_current(self):
        if self.current_chat:
            CHATS_DIR.mkdir(parents=True, exist_ok=True)
            self._chat_path(self.current_chat["id"]).write_text(
                json.dumps(self.current_chat, indent=2))

    def new_chat(self):
        self._stop_worker()
        now = datetime.now().isoformat(timespec="seconds")
        chat = {"id": now.replace(":", "-").replace(".", "-"),
                "title": "Nuova chat", "messages": [], "created": now}
        self.chats.insert(0, chat)
        self.current_chat = chat
        self._refresh_chat_list()
        self.stack.setCurrentIndex(0)

    def _open_chat(self, item):
        self._stop_worker()
        chat_id = item.data(Qt.UserRole)
        self.current_chat = next(c for c in self.chats if c["id"] == chat_id)
        self._render()
        self.stack.setCurrentIndex(1)

    # ------------------------------------------------------------- motore UI

    def _engine_changed(self, *_):
        self.settings["engine"] = self.engine_combo.currentData()
        try:
            self.model_combo.currentTextChanged.disconnect(self._model_changed)
        except Exception:
            pass
        self.model_combo.clear()
        fallback = (["devstral-small-2:24b", "codestral:22b", "mistral-small3.2:24b"]
                    if self.settings["engine"] == "ollama"
                    else ["mistral-medium-latest", "mistral-large-latest",
                          "devstral-latest", "codestral-latest"])
        self.model_combo.addItems(fallback)
        saved = self.settings.get("model_ollama" if self.settings["engine"] == "ollama"
                                  else "model_mistral")
        i = self.model_combo.findText(saved)
        if i >= 0:
            self.model_combo.setCurrentIndex(i)
        self.model_combo.currentTextChanged.connect(self._model_changed)

    def _model_changed(self, text):
        key = "model_ollama" if self.settings["engine"] == "ollama" else "model_mistral"
        self.settings[key] = text
        save_settings(self.settings)

    def refresh_models(self):
        try:
            if self.settings["engine"] == "ollama":
                models = list_ollama_models(self.settings["ollama_host"])
            else:
                key = self.settings["mistral_api_key"]
                if not key:
                    QMessageBox.warning(self, APP_NAME,
                                        "Inserisci prima l'API key nelle impostazioni.")
                    return
                models = list_mistral_models(key)
            if models:
                self.model_combo.clear()
                self.model_combo.addItems(models)
                self.status.setText(f"{len(models)} modelli disponibili ⚡")
        except Exception as e:  # noqa: BLE001
            QMessageBox.warning(self, APP_NAME, f"Impossibile elencare i modelli:\n{e}")

    def open_settings(self):
        dlg = SettingsDialog(self.settings, self)
        if dlg.exec():
            self.settings = dlg.values()
            save_settings(self.settings)
            if self.settings["engine"] == "mistral":
                self.engine_combo.setCurrentIndex(1)
            else:
                self.engine_combo.setCurrentIndex(0)
            self.status.setText("Impostazioni salvate ✓")

    # -------------------------------------------------------------- messaging

    def quick_send(self, text):
        if self.current_chat is None:
            self.new_chat()
        self.stack.setCurrentIndex(1)
        self.send(text)

    def _render(self):
        if not self.current_chat:
            return
        label = (self.settings["model_ollama"] if self.settings["engine"] == "ollama"
                 else self.settings["model_mistral"])
        self.view.setHtml(chat_html(self.current_chat["messages"], label))
        sb = self.view.verticalScrollBar()
        sb.setValue(sb.maximum())

    def _on_send(self):
        self.send(self.input.toPlainText().strip())

    def send(self, text):
        if not text or (self.worker and self.worker.isRunning()):
            return
        if self.current_chat is None:
            self.new_chat()
        chat = self.current_chat
        chat["messages"].append({"role": "user", "content": text})
        if chat["title"] == "Nuova chat":
            chat["title"] = text[:42]
            self._refresh_chat_list()
        chat["messages"].append({"role": "assistant", "content": "",
                                  "model": self.model_combo.currentText()})
        self.input.clear()
        self._render()

        sys_prompt = self.settings.get("system_prompt", "")
        history = ([{"role": "system", "content": sys_prompt}]
                    if sys_prompt else [])
        for m in chat["messages"]:
            if m["role"] == "user" or m["content"]:
                history.append({"role": m["role"], "content": m["content"]})

        self.worker = ChatWorker(self.settings, history)
        self.worker.chunk.connect(self._on_chunk)
        self.worker.finished_ok.connect(self._on_done)
        self.worker.failed.connect(self._on_error)
        self.send_btn.setText("■ Stop")
        self.send_btn.clicked.disconnect()
        self.send_btn.clicked.connect(self._stop_worker)
        self.worker.start()

    def _on_chunk(self, piece):
        self.current_chat["messages"][-1]["content"] += piece
        self._render()

    def _on_done(self):
        self._finish_turn()

    def _on_error(self, msg):
        chat = self.current_chat
        if chat and chat["messages"][-1]["content"] == "":
            chat["messages"][-1]["content"] = f"⚠️ {msg}"
        self._render()
        self._finish_turn()

    def _stop_worker(self):
        if self.worker and self.worker.isRunning():
            self.worker.stop()
            self.worker.wait(2000)
        self._finish_turn()

    def _finish_turn(self):
        self._save_current()
        try:
            self.send_btn.clicked.disconnect()
        except Exception:
            pass
        self.send_btn.setText("Invia ▲")
        self.send_btn.clicked.connect(self._on_send)

    def eventFilter(self, obj, event):
        if obj is self.input and event.type() == event.KeyPress:
            if event.key() in (Qt.Key_Return, Qt.Key_Enter) and not (
                    event.modifiers() & Qt.ShiftModifier):
                self._on_send()
                return True
        return super().eventFilter(obj, event)

    def closeEvent(self, e):
        self._stop_worker()
        self._save_current()
        super().closeEvent(e)


def main():
    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setOrganizationName(ORG)
    f = QFont()
    f.setFamilies(["Ubuntu Sans", "Inter", "Noto Sans"])
    f.setPointSize(11)
    app.setFont(f)
    win = MainWindow()
    win.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
