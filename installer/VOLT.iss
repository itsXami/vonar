; VOLT Windows installer (Inno Setup 6). Built by CI (.github/workflows/ci.yml, Windows job):
;   iscc /DAppVersion=0.9.0 /DSourceDir=<folder with VOLT.vst3> installer\VOLT.iss
; Output: installer\Output\VOLT-<version>-Setup.exe
;
; Wizard (English): welcome -> licence (AGPLv3) -> install -> finish. Installs the VST3 plugin only (the
; standalone app was dropped at the user's request) into the standard folder every host scans
; (Common Files\VST3), so FL Studio finds it. A licence copy goes to Program Files\VOLT.
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
UninstallDisplayIcon={app}\volt.ico
DisableDirPage=yes
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
Name: "en"; MessagesFile: "compiler:Default.isl"

[Files]
Source: "{#SourceDir}\VOLT.vst3\*"; DestDir: "{commoncf64}\VST3\VOLT.vst3"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "volt.ico"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\LICENSE"; DestDir: "{app}"; DestName: "LICENSE.txt"; Flags: ignoreversion

[UninstallDelete]
Type: filesandordirs; Name: "{commoncf64}\VST3\VOLT.vst3"
