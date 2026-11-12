[Setup]
AppName=Renomeador Pro
AppVersion=1.1
AppPublisher=Fornecedor TI
DefaultDirName={autopf}\Renomeador Pro
DefaultGroupName=Renomeador Pro
AllowNoIcons=yes

; AGORA ISSO AQUI VAI FUNCIONAR PERFEITAMENTE!
SetupIconFile=icon.ico

UninstallDisplayIcon={app}\RenomeadorPro.exe
Compression=lzma2/max
SolidCompression=yes
OutputDir=Output
OutputBaseFilename=Instalador_RenomeadorPro_v1.0
WizardStyle=modern

[Tasks]
Name: "desktopicon"; Description: "Criar um atalho na Area de Trabalho"; GroupDescription: "Icones Adicionais:"

[Files]
Source: "dist\RenomeadorPro.exe"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
; Como o EXE agora tem o ícone embutido, o atalho puxa o ícone sozinho, sem bugar!
Name: "{group}\Renomeador Pro"; Filename: "{app}\RenomeadorPro.exe"
Name: "{group}\Desinstalar Renomeador Pro"; Filename: "{uninstallexe}"
Name: "{autodesktop}\Renomeador Pro"; Filename: "{app}\RenomeadorPro.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\RenomeadorPro.exe"; Description: "Iniciar o Renomeador Pro agora"; Flags: nowait postinstall skipifsilent