# Ricetta PyInstaller per Mistral Desktop
# Dice a PyInstaller come impacchettare main.py con dentro tutto Qt WebEngine.

from PyInstaller.utils.hooks import collect_all

# Porta dentro TUTTO PySide6, Chromium incluso: pesante ma a prova di errore
datas, binaries, hiddenimports = [], [], []
for d, b, h in (collect_all("PySide6"),):
    datas += d
    binaries += b
    hiddenimports += h

a = Analysis(
    ["main.py"],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    excludes=["tkinter"],
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    exclude_binaries=True,
    name="MistralDesktop",
    console=False,   # niente finestra nera di debug: è un'app vera
)

coll = COLLECT(exe, a.binaries, a.datas, name="MistralDesktop")