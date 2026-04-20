; AIra Pro Photobooth System - Inno Setup Installer Script
; Download Inno Setup: https://jrsoftware.org/isdl.php

#define MyAppName "AIra Pro Photobooth"
#define MyAppVersion "2.1"
#define MyAppPublisher "AIra Systems"
#define MyAppExeName "AIraPhotobooth.exe"
#define MyAppURL "https://github.com/yourusername/AIra-Photobooth-System"
#define MyAppAssocName "AIra Photobooth Session"
#define MyAppAssocExt ".photobooth"

[Setup]
; NOTE: The value of AppId uniquely identifies this application.
AppId={{A1B2C3D4-E5F6-7890-ABCD-EF1234567890}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
AllowNoIcons=yes
LicenseFile=
OutputDir=installer_output
OutputBaseFilename=AIraPhotobooth_Setup_v{#MyAppVersion}
SetupIconFile=assets\app_icon.ico
Compression=lzma2/ultra64
SolidCompression=yes
WizardStyle=modern
WizardImageFile=
WizardSmallImageFile=
PrivilegesRequired=lowest
ArchitecturesAllowed=x64
ArchitecturesInstallIn64BitMode=x64

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "quicklaunchicon"; Description: "{cm:CreateQuickLaunchIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked; OnlyBelowVersion: 6.1; Check: not IsAdminInstallMode

[Files]
; Main executable
Source: "dist\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion

; Cloudflare Tunnel (optional - only if exists)
Source: "dist\cloudflared.exe"; DestDir: "{app}"; Flags: ignoreversion skipifsourcedoesntexist

; Configuration files
Source: "config.json"; DestDir: "{app}"; Flags: ignoreversion

; Icon file
Source: "assets\app_icon.ico"; DestDir: "{app}"; Flags: ignoreversion

; Frame templates
Source: "frames\*"; DestDir: "{app}\frames"; Flags: ignoreversion recursesubdirs createallsubdirs

; Assets (logos, icons)
Source: "assets\*"; DestDir: "{app}\assets"; Flags: ignoreversion recursesubdirs createallsubdirs

; NOTE: Don't use "Flags: ignoreversion" on any shared system files

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon
Name: "{userappdata}\Microsoft\Internet Explorer\Quick Launch\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: quicklaunchicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

[Code]
function InitializeSetup(): Boolean;
begin
  Result := True;
end;

procedure CurStepChanged(CurStep: TSetupStep);
begin
  if CurStep = ssPostInstall then
  begin
    // Any post-installation tasks can go here
    // For example, creating initial directories
    if not DirExists(ExpandConstant('{app}\events\output')) then
      ForceDirectories(ExpandConstant('{app}\events\output'));
    if not DirExists(ExpandConstant('{app}\events\raw')) then
      ForceDirectories(ExpandConstant('{app}\events\raw'));
    if not DirExists(ExpandConstant('{app}\logs')) then
      ForceDirectories(ExpandConstant('{app}\logs'));
  end;
end;
