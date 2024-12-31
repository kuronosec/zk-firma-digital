; -- 64Bit.iss --
; Demonstrates installation of a program built for the x64 (a.k.a. AMD64)
; architecture.
; To successfully run this installation and the program it installs,
; you must have a "x64" edition of Windows.

; SEE THE DOCUMENTATION FOR DETAILS ON CREATING .ISS SCRIPT FILES!

[Setup]
AppName=ZK Firma Digital
AppVersion=0.5
WizardStyle=modern
DefaultDirName={autopf}\zk-firma-digital
DefaultGroupName=ZK Firma Digital
UninstallDisplayIcon={app}\zk-firma-digital.exe
Compression=lzma2
SolidCompression=yes
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible

[Files]
Source: "zk-artifacts\*"; DestDir: "{app}\zk-artifacts"; Flags: recursesubdirs createallsubdirs
Source: "CA-certificates\*"; DestDir: "{app}\CA-certificates";
Source: "node.exe" ; DestDir: "{app}"; Flags: ignoreversion
Source: "snarkjs.cmd" ; DestDir: "{app}"; Flags: ignoreversion
Source: "node_modules\*"; DestDir: "{app}\node_modules"; Flags: recursesubdirs createallsubdirs
Source: "zk-firma-digital.exe"; DestDir: "{app}"; DestName: "zk-firma-digital.exe"

[Icons]
Name: "{group}\ZK Firma Digital"; Filename: "{app}\zk-firma-digital.exe"
