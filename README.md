<div align="center">

# ✦ Mistral Desktop

**Client desktop non ufficiale per Mistral AI**

*Una app made in Italy 🇮🇹, con l'IA della Francia 🇫🇷, per tutta l'Europa 🇪🇺*

Chat con i modelli Mistral direttamente dal tuo desktop — gratis, open source e rispettoso della privacy.

[![Get it from the Snap Store](https://snapcraft.io/static/images/badges/en/snap-store-black.svg)](https://snapcraft.io/mistral-desktop)

</div>

## ✨ Caratteristiche

- 🦙 **Ollama locale** — gratis, privato, funziona offline
- ☁️ **API Mistral** — i modelli ufficiali nel cloud
- 🔀 Switch motore con un clic, modelli rilevati automaticamente
- ⚡ Core di streaming in **Rust** (PyO3) — opzionale, usato in automatico se installato
- 🗂️ Cronologia chat salvata in locale
- 🎨 Tema scuro in stile Mistral
- 🌍 Linux (Snap + AppImage), Windows (installer), macOS (.dmg)

## 📦 Installazione

```bash
# da Snap Store (appena pubblicato)
sudo snap install mistral-desktop

# da sorgente (Ubuntu/Debian: servono venv e una libreria richiesta da Qt)
sudo apt install python3-venv libxcb-cursor0
git clone https://github.com/RubenNovello/mistral-desktop.git
cd mistral-desktop
python3 -m venv .venv && source .venv/bin/activate
pip install PySide6 requests
python mistral_desktop.py
```

Se compare l'errore `Could not load the Qt platform plugin "xcb"`, manca `libxcb-cursor0`
(comando `apt` qui sopra).

## ⚡ Core Rust (opzionale, prestazioni massime)

```bash
pip install maturin
maturin build --release
pip install target/wheels/*.whl
```

L'app rileva il core Rust da sola (vedrai "core: Rust ⚡" nella barra di stato).

## 🔧 Requisiti

- [Ollama](https://ollama.com) in esecuzione (`ollama serve`), **oppure** una [API key Mistral](https://console.mistral.ai)

## 🐦 Filosofia

Questo progetto nasce da una filosofia completamente **Open**: Open Minded, Open Source, Free/Libre.

- Chiunque può **scaricare, usare, modificare e migliorare** questa app, liberamente
- Nessun costo, nessun lock-in, nessun telemetry: il codice è lì, leggilo tutto
- Se ti è utile, puoi **ringraziare** con una ⭐ su GitHub, un issue ben scritto, o una pull request: le PR sono il "grazie" più bello
- Se una cosa non c'è ancora… questo è esattamente il motivo per cui esiste: per aggiungerla, insieme

> Nota: su Windows e macOS il sistema può mostrare un avviso al primo avvio
> ("sviluppatore non verificato"). Non è un avviso di virus: è solo la
> richiesta delle piattaforme di un certificato a pagamento. Il codice sorgente
> è pubblico e verificabile da chiunque — la fiducia nasce da quello.

## ⚖️ Avvertenze

Progetto community, **non affiliato a Mistral AI**. Il marchio è usato a solo
scopo identificativo del client. Licenza MIT.

## 🇪🇺 English summary

Mistral Desktop is an unofficial, community-made desktop client for Mistral AI.
Made in Italy 🇮🇹, with AI from France 🇫🇷, for all of Europe 🇪🇺 (and beyond).
