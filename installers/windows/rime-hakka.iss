; Inno Setup script for rime-hakka (Weasel schema package)
; Build with:  iscc installers\windows\rime-hakka.iss
; CI version override: iscc "/DAppVersion=X.Y.Z" installers\windows\rime-hakka.iss
;
; Weasel dependency behaviour
; ─────────────────────────────
; If Weasel is already installed, setup proceeds directly.
; If Weasel is missing, a download page fetches the official installer
; (~12 MB) and runs it silently — users see only a Windows UAC prompt.
;
; To bundle Weasel instead of downloading it at install time:
;   1. Download the installer to installers\windows\{#WeaselInstaller}
;   2. Uncomment the [Files] entry tagged "BUNDLE OPTION" below.
;   3. Comment out the download block in PrepareToInstall() in [Code].

#define AppName          "Rime Hakka (Huiyang)"
; Allow CI to inject version via: iscc /DAppVersion=X.Y.Z
#ifndef AppVersion
  #define AppVersion     "0.1.0"
#endif
#define AppPublisher     "rime-hakka contributors"
#define SchemaId         "hakka_huiyang"

; Update both defines when a new Weasel release is available.
; Releases: https://github.com/rime/weasel/releases
#define WeaselVersion    "0.17.4"
#define WeaselInstaller  "weasel-0.17.4.0-installer.exe"
#define WeaselURL        "https://github.com/rime/weasel/releases/download/" \
                         + WeaselVersion + "/" + WeaselInstaller

[Setup]
AppName={#AppName}
AppVersion={#AppVersion}
AppPublisher={#AppPublisher}
DefaultDirName={userappdata}\Rime
DisableDirPage=yes
DisableProgramGroupPage=yes
Uninstallable=yes
OutputBaseFilename=hakka-huiyang-rime-v{#AppVersion}-setup
OutputDir=..\..\dist
; Schema files live in %APPDATA%\Rime — no admin needed.
; The Weasel dependency installer handles its own UAC elevation.
PrivilegesRequired=lowest
Compression=lzma
SolidCompression=yes
WizardStyle=modern

[Tasks]
Name: setschema; Description: "Set Hakka (Huiyang) as the only active input schema (recommended)"; Flags: checked

[Files]
Source: "..\..\schemas\huiyang\hakka_huiyang.schema.yaml"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\..\schemas\huiyang\hakka_huiyang.dict.yaml";   DestDir: "{app}"; Flags: ignoreversion
; Restricts Rime to only the Hakka schema — written when the task above is ticked.
Source: "default.custom.yaml"; DestDir: "{app}"; Flags: ignoreversion; Tasks: setschema
; BUNDLE OPTION — uncomment to embed the Weasel installer instead of downloading it:
;Source: "{#WeaselInstaller}"; DestDir: "{tmp}"; Flags: deleteafterinstall nocompression

[Run]
; Trigger Weasel to rebuild the prism after the schema files are in place.
; GetWeaselDeployer() resolves the path from the registry (handles both
; native and WOW64 registry hives).
Filename: "{code:GetWeaselDeployer}"; \
    Parameters: "/deploy"; Flags: postinstall skipifsilent runhidden; \
    Description: "Deploy Rime schema (rebuilds the input method)"; \
    Check: WeaselDeployerExists

[UninstallDelete]
Type: files; Name: "{app}\hakka_huiyang.schema.yaml"
Type: files; Name: "{app}\hakka_huiyang.dict.yaml"
Type: files; Name: "{app}\default.custom.yaml"

[Messages]
FinishedLabel=Installation complete.%n%nRight-click the Weasel tray icon → Schema List → tick "惠陽客家話 (Hagfa Pinyim)".

[Code]

var
  WeaselDownloadPage: TDownloadWizardPage;

// ── Registry helpers ───────────────────────────────────────────────────────

function GetWeaselRoot: String;
// Returns the WeaselRoot install directory, or '' if not found.
// Checks both the native hive and the WOW6432Node hive (32-bit Weasel on 64-bit Windows).
var
  Root: String;
begin
  if RegQueryStringValue(HKLM, 'SOFTWARE\Rime\Weasel', 'WeaselRoot', Root) then
    Result := Root
  else if RegQueryStringValue(HKLM, 'SOFTWARE\WOW6432Node\Rime\Weasel', 'WeaselRoot', Root) then
    Result := Root
  else
    Result := '';
end;

function WeaselInstalled: Boolean;
begin
  Result := GetWeaselRoot <> '';
end;

function WeaselDeployerExists: Boolean;
begin
  Result := FileExists(GetWeaselRoot + '\WeaselDeployer.exe');
end;

function GetWeaselDeployer(Param: String): String;
begin
  Result := GetWeaselRoot + '\WeaselDeployer.exe';
end;

// ── Download page setup ────────────────────────────────────────────────────

procedure InitializeWizard;
begin
  WeaselDownloadPage := CreateDownloadPage(
    'Installing Weasel',
    'Downloading the Rime input method engine for Windows…',
    nil);
end;

// ── Weasel prerequisite check and install ─────────────────────────────────

function PrepareToInstall(var NeedsRestart: Boolean): String;
// Called after "Ready to Install". Return '' to proceed, or an error message
// to halt setup and display the message on the Preparing page.
var
  TempInstaller: String;
  ResultCode: Integer;
begin
  Result := '';

  if WeaselInstalled then
    Exit; // Already present — nothing to do.

  if MsgBox(
    'Weasel (the Rime input method for Windows) is not installed.' + #13#10#13#10 +
    'Weasel is required to use the Hakka input schema.' + #13#10 +
    'Click OK to download and install it now (~12 MB).' + #13#10#13#10 +
    'You will see a Windows security prompt — click Yes to allow the install.',
    mbConfirmation, MB_OKCANCEL) <> IDOK then
  begin
    Result :=
      'Weasel is required. Install it from https://rime.im/download/ ' +
      'then re-run this setup.';
    Exit;
  end;

  // ── Download ──
  WeaselDownloadPage.Clear;
  WeaselDownloadPage.Add('{#WeaselURL}', '{#WeaselInstaller}', '');
  WeaselDownloadPage.Show;
  try
    WeaselDownloadPage.Download;
  except
    WeaselDownloadPage.Hide;
    Result :=
      'Download failed: ' + GetExceptionMessage + #13#10 +
      'Please install Weasel manually from https://rime.im/download/';
    Exit;
  end;
  WeaselDownloadPage.Hide;

  // ── Run the Weasel installer silently ──
  // /S = NSIS silent mode (no UI, only the UAC elevation prompt).
  TempInstaller := ExpandConstant('{tmp}\{#WeaselInstaller}');
  if not ShellExec('', TempInstaller, '/S', '', SW_HIDE,
                   ewWaitUntilTerminated, ResultCode) then
  begin
    Result :=
      'Could not launch the Weasel installer.' + #13#10 +
      'Please install Weasel manually from https://rime.im/download/';
    Exit;
  end;

  if ResultCode <> 0 then
  begin
    Result :=
      'Weasel installation exited with code ' + IntToStr(ResultCode) + '.' + #13#10 +
      'Install Weasel from https://rime.im/download/ then re-run this setup.';
    Exit;
  end;

  // Final sanity check — confirm registry key is present.
  if not WeaselInstalled then
    Result :=
      'Weasel does not appear to be installed after setup.' + #13#10 +
      'Please install it from https://rime.im/download/ then re-run.';
end;
