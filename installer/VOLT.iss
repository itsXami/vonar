; VOLT Windows installer (Inno Setup 6). Built by CI (.github/workflows/ci.yml, Windows job):
;   iscc /DAppVersion=0.9.0 /DSourceDir=<folder with VOLT.vst3 and VOLT.exe> installer\VOLT.iss
; Output: installer\Output\VOLT-<version>-Setup.exe
;
; Wizard: welcome -> licence (AGPLv3) -> components (VST3, Standalone) -> folder for the Standalone ->
; shortcuts -> install -> finish (option to start VOLT). Polish or English, from the Windows language.
; The VST3 always goes to the standard folder every host scans (Common Files\VST3), so FL Studio finds it.
; Factory presets are built into the plugin; user presets in %APPDATA%\VOLT are never touched by uninstall.

#ifndef AppVersion
  #define AppVersion "0.0.0"
#endif
#ifndef SourceDir
  #define SourceDir "..\dist"
#endif

[Setup]
AppId={{C69A1C62-E46F-498C-BCB2-D48D5602891C}
AppName=VOLT
AppVersion={#AppVersion}
AppVerName=VOLT {#AppVersion}
AppPublisher=VOLT
AppPublisherURL=https://github.com/jakubnikapiotr-design/vst
AppSupportURL=https://github.com/jakubnikapiotr-design/vst/issues
DefaultDirName={autopf}\VOLT
DefaultGroupName=VOLT
DisableProgramGroupPage=yes
LicenseFile=..\LICENSE
OutputDir=Output
OutputBaseFilename=VOLT-{#AppVersion}-Setup
SetupIconFile=volt.ico
UninstallDisplayIcon={app}\VOLT.exe
WizardStyle=modern
WizardImageFile=wizard-large.bmp
WizardSmallImageFile=wizard-small.bmp
Compression=lzma2/max
SolidCompression=yes
ArchitecturesAllowed=x64
ArchitecturesInstallIn64BitMode=x64
PrivilegesRequired=admin
MinVersion=10.0
CloseApplications=yes

[Languages]
Name: "pl"; MessagesFile: "compiler:Languages\Polish.isl"
Name: "en"; MessagesFile: "compiler:Default.isl"

[CustomMessages]
pl.CompVst3=Plugin VST3 (FL Studio i inne programy DAW)
en.CompVst3=VST3 plugin (FL Studio and other DAWs)
pl.CompStandalone=Samodzielny program VOLT (bez DAW)
en.CompStandalone=VOLT standalone application (no DAW needed)
pl.TypeFull=Pełna instalacja
en.TypeFull=Full installation
pl.TypePlugin=Tylko plugin VST3
en.TypePlugin=VST3 plugin only
pl.TypeCustom=Wybór składników
en.TypeCustom=Custom installation

[Types]
Name: "full"; Description: "{cm:TypeFull}"
Name: "plugin"; Description: "{cm:TypePlugin}"
Name: "custom"; Description: "{cm:TypeCustom}"; Flags: iscustom

[Components]
Name: "vst3"; Description: "{cm:CompVst3}"; Types: full plugin custom
Name: "standalone"; Description: "{cm:CompStandalone}"; Types: full custom

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Components: standalone; Flags: unchecked

[Files]
Source: "{#SourceDir}\VOLT.vst3\*"; DestDir: "{commoncf64}\VST3\VOLT.vst3"; Components: vst3; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "{#SourceDir}\VOLT.exe"; DestDir: "{app}"; Components: standalone; Flags: ignoreversion
Source: "..\LICENSE"; DestDir: "{app}"; DestName: "LICENSE.txt"; Flags: ignoreversion

[Icons]
Name: "{autoprograms}\VOLT"; Filename: "{app}\VOLT.exe"; Components: standalone
Name: "{autodesktop}\VOLT"; Filename: "{app}\VOLT.exe"; Components: standalone; Tasks: desktopicon

[Run]
Filename: "{app}\VOLT.exe"; Description: "{cm:LaunchProgram,VOLT}"; Components: standalone; Flags: nowait postinstall skipifsilent unchecked

[UninstallDelete]
Type: filesandordirs; Name: "{commoncf64}\VST3\VOLT.vst3"
