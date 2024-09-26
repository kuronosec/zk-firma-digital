; -- 64Bit.iss --
; Demonstrates installation of a program built for the x64 (a.k.a. AMD64)
; architecture.
; To successfully run this installation and the program it installs,
; you must have a "x64" edition of Windows.

; SEE THE DOCUMENTATION FOR DETAILS ON CREATING .ISS SCRIPT FILES!

[Setup]
AppName=Cliente FVA
AppVersion=1.5
WizardStyle=modern
DefaultDirName={autopf}\Cliente FVA
DefaultGroupName=Firma Digital
UninstallDisplayIcon={app}\client_fva.exe
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
Source: "client_fva.exe"; DestDir: "{app}"; DestName: "client_fva.exe"
Source: "icon.png"; DestDir: "{app}"; DestName: "icon.png"
Source: "asepkcs.dll"; DestDir: "{autopf}\System32"; DestName: "asepkcs.dll"; Flags: onlyifdoesntexist 
Source: "asepkcs.dll"; DestDir: "{app}\os_libs\windows\"; DestName: "asepkcs.dll"; Flags: onlyifdoesntexist recursesubdirs createallsubdirs

[Icons]
Name: "{group}\Cliente FVA"; Filename: "{app}\client_fva.exe"


