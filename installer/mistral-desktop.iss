; Inno Setup script per Mistral Desktop (Windows installer)
; Build: ISCC installer\mistral-desktop.iss  (richiede dist\MistralDesktop\ da PyInstaller)

[Setup]
AppName=Mistral Desktop
AppVersion=0.1.0
AppPublisher=mistral-desktop-community (unofficial client)
DefaultDirName={autopf}\Mistral Desktop
DefaultGroupName=Mistral Desktop
OutputDir=dist
OutputBaseFilename=MistralDesktop-setup
PrivilegesRequired=lowest
Compression=lzma2
SolidCompression=yes
WizardStyle=modern

[Files]
Source: "dist\MistralDesktop\*"; DestDir: "{app}"; Flags: recursesubdirs

[Icons]
Name: "{autoprograms}\Mistral Desktop"; Filename: "{app}\MistralDesktop.exe"
Name: "{autodesktop}\Mistral Desktop";  Filename: "{app}\MistralDesktop.exe"

[Run]
Filename: "{app}\MistralDesktop.exe"; Description: "Avvia Mistral Desktop"; Flags: nowait postinstall skipifsilent
