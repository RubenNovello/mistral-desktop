<div align="center">

# Mistral Desktop

**Client desktop non ufficiale per Mistral AI**

*Una app made in Italy 🇮🇹, con l'IA della Francia 🇫🇷, per tutta l'Europa 🇪🇺*

🇮🇹 **Italiano**   🇬🇧 English

La chat di Mistral AI in una finestra dedicata sul desktop — gratis, open source, zero API key.

[![Get it from the Snap Store](https://snapcraft.io/static/images/badges/en/snap-store-black.svg)](https://snapcraft.io/mistral-desktop)

</div>

## 🖥️ Cos'è

Mistral Desktop apre **chat.mistral.ai** in una finestra nativa (PySide6/Qt): niente browser, niente API key, niente configurazione. Accedi una volta con Google o Apple e la sessione resta — ogni avvio ti ritrovi già dentro, pronto a chattare.

## ✨ Caratteristiche

- 🚀 **Finestra dedicata** — la chat sempre a portata di clic, senza tab e senza distrazioni
- 🔐 **Login persistente** — Google/Apple, sessione salvata in locale (`~/.local/share/mistral-desktop/`)
- ⚡ **Più fluida del browser** — un solo scopo, zero il peso di un browser completo
- 🔒 **Privacy** — profilo e dati restano sul tuo computer, nessun telemetry
- 🎨 **Qt 6 nativo** — finestra pulita, tema scuro in stile Mistral
- 🐧 **Linux**: Snap Store + sorgente, open source (MIT)

## 📦 Installazione

**Da Snap Store (consigliato):**

```bash
sudo snap install mistral-desktop
```

oppure cerca "Mistral Desktop" nell'App Centre / Ubuntu Software.

**Da sorgente (Ubuntu/Debian):**

```bash
sudo apt install python3-venv libxcb-cursor0
git clone https://github.com/RubenNovello/mistral-desktop.git
cd mistral-desktop
python3 -m venv .venv && source .venv/bin/activate
pip install PySide6
python main.py
```

Se compare l'errore `Could not load the Qt platform plugin "xcb"`, manca `libxcb-cursor0`
(comando `apt` qui sopra).

## 🐦 Filosofia

Questo progetto nasce da una filosofia completamente **Open**: Open Minded, Open Source, Free/Libre.

- Chiunque può **scaricare, usare, modificare e migliorare** questa app, liberamente
- Nessun costo, nessun lock-in, nessun telemetry: il codice è lì, leggilo tutto
- Se ti è utile, puoi **ringraziare** con una ⭐ su GitHub, un issue ben scritto, o una pull request: le PR sono il "grazie" più bello
- Se una cosa non c'è ancora… questo è esattamente il motivo per cui esiste: per aggiungerla, insieme

## ⚖️ Avvertenze

Progetto community, **non affiliato a Mistral AI**. Il marchio è usato a solo
scopo identificativo del client. Licenza MIT.

## 🇪🇺 English summary

Mistral Desktop is an unofficial, community-made desktop client for Mistral AI:
chat.mistral.ai in a dedicated window, no API key, no setup — just log in once.
Made in Italy 🇮🇹, with AI from France 🇫🇷, for all of Europe 🇪🇺 (and beyond).

<div align="center">

# Mistral Desktop

**Unofficial desktop client for Mistral AI**

*An app made in Italy 🇮🇹, with AI from France 🇫🇷, for all of Europe 🇪🇺*

The Mistral AI chat in a dedicated desktop window — free, open source, zero API keys.

🇮🇹 Italiano   🇬🇧 **English**

[![Get it from the Snap Store](https://snapcraft.io/static/images/badges/en/snap-store-black.svg)](https://snapcraft.io/mistral-desktop)

</div>

## 🖥️ What is it?

Mistral Desktop opens **chat.mistral.ai** in a native window (PySide6/Qt): no browser, no API keys, no setup. Log in once with Google or Apple and your session persists — every launch drops you right back into the conversation.

## ✨ Features

- 🚀 **A dedicated window** — your chat one click away, no tabs, no distractions
- 🔐 **Persistent login** — Google/Apple, session stored locally (`~/.local/share/mistral-desktop/`)
- ⚡ **Smoother than a browser** — it does one thing, without the weight of a full browser
- 🔒 **Privacy** — your profile and data stay on your computer, no telemetry
- 🎨 **Native Qt 6** — clean window, Mistral-style dark theme
- 🐧 **Linux**: Snap Store + source, open source (MIT)

## 📦 Installation

**From the Snap Store (recommended):**

```bash
sudo snap install mistral-desktop
```

or search for "Mistral Desktop" in the App Centre / Ubuntu Software.

**From source (Ubuntu/Debian):**

```bash
sudo apt install python3-venv libxcb-cursor0
git clone https://github.com/RubenNovello/mistral-desktop.git
cd mistral-desktop
python3 -m venv .venv && source .venv/bin/activate
pip install PySide6
python main.py
```

If you get the error `Could not load the Qt platform plugin "xcb"`, you are missing
`libxcb-cursor0` (see the `apt` command above).

## 🐦 Philosophy

This project was born from a fully **Open** philosophy: Open Minded, Open Source, Free/Libre.

- Anyone can **download, use, modify and improve** this app, freely
- No cost, no lock-in, no telemetry: the code is right there, read it all
- If you find it useful, you can say **thanks** with a ⭐ on GitHub, a well-written
  issue, or a pull request: PRs are the nicest "thank you" of all
- If something doesn't exist yet… that is exactly why this project exists:
  to add it, together

## ⚖️ Disclaimer

Community project, **not affiliated with Mistral AI**. The trademark is used
purely to identify the client. MIT license.

---

*Made in Italy 🇮🇹, with AI from France 🇫🇷, for all of Europe 🇪🇺 (and beyond).*
