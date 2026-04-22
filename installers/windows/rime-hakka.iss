; Inno Setup script for rime-hakka (Weasel schema package)
; Build with:  iscc installers\windows\rime-hakka.iss
; Requires the release artifacts under ..\..\dist\ (produced by build/package.py).

#define AppName       "Rime Hakka (Huiyang)"
#define AppVersion    "0.1.0"
#define AppPublisher  "rime-hakka contributors"
#define SchemaId      "hakka_huiyang"

[Setup]
AppName={#AppName}
AppVersion={#AppVersion}
AppPublisher={#AppPublisher}
DefaultDirName={userappdata}\Rime
DisableDirPage=yes
DisableProgramGroupPage=yes
Uninstallable=yes
OutputBaseFilename=hakka-huiyang-rime-v{#AppVersion}-setup
PrivilegesRequired=lowest
Compression=lzma
SolidCompression=yes
WizardStyle=modern

[Files]
Source: "..\..\schemas\huiyang\hakka_huiyang.schema.yaml"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\..\schemas\huiyang\hakka_huiyang.dict.yaml";   DestDir: "{app}"; Flags: ignoreversion

[Run]
; Trigger Weasel to rebuild the prism after install.
; WeaselRoot is set in the registry by the Weasel installer.
Filename: "{reg:HKLM\SOFTWARE\Rime\Weasel,WeaselRoot}\WeaselDeployer.exe"; \
    Parameters: "/deploy"; Flags: postinstall skipifsilent runhidden; \
    Description: "Deploy Rime schema"; \
    Check: RegValueExists(HKLM, 'SOFTWARE\Rime\Weasel', 'WeaselRoot')

[UninstallDelete]
Type: files; Name: "{app}\hakka_huiyang.schema.yaml"
Type: files; Name: "{app}\hakka_huiyang.dict.yaml"

[Messages]
FinishedLabel=Installation complete.%n%nRight-click the Weasel tray icon → Schema List → tick "惠陽客家話 (Hagfa Pinyim)".
