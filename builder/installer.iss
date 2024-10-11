; -- 64Bit.iss --
; Demonstrates installation of a program built for the x64 (a.k.a. AMD64)
; architecture.
; To successfully run this installation and the program it installs,
; you must have a "x64" edition of Windows.

; SEE THE DOCUMENTATION FOR DETAILS ON CREATING .ISS SCRIPT FILES!

[Setup]
AppName=ZK Firma Digital
AppVersion=0.2
WizardStyle=modern
DefaultDirName={autopf}\zk-firma-digital
DefaultGroupName=ZK Firma Digital
UninstallDisplayIcon={app}\zk-firma-digital.exe
Compression=lzma2
SolidCompression=yes
;OutputDir=userdocs:Inno Setup Examples Output
; "ArchitecturesAllowed=x64" specifies that Setup cannot run on
; anything but x64.
ArchitecturesAllowed=x64
; "ArchitecturesInstallIn64BitMode=x64" requests that the install be
; done in "64-bit mode" on x64, meaning it should use the native
; 64-bit Program Files directory and the 64-bit view of the registry.
ArchitecturesInstallIn64BitMode=x64

[Files]
Source: "zk-artifacts\*"; DestDir: "{app}\zk-artifacts";
Source: "zk-artifacts\firma-verifier_js\*"; DestDir: "{app}\zk-artifacts\firma-verifier_js";
Source: "CA-certificates\*"; DestDir: "{app}\CA-certificates";
Source: "zk-firma-digital.exe"; DestDir: "{app}"; DestName: "zk-firma-digital.exe"

[Icons]
Name: "{group}\ZK Firma Digital"; Filename: "{app}\zk-firma-digital.exe"
