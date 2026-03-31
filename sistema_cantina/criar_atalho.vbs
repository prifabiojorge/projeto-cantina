Set WshShell = CreateObject("WScript.Shell")
DesktopPath = WshShell.SpecialFolders("Desktop")
Set oShortcut = WshShell.CreateShortcut(DesktopPath & "\Cantina.lnk")
oShortcut.TargetPath = "E:\Documents\DEGOO\CANTINA\sistema_cantina\INICIAR_CANTINA.bat"
oShortcut.WorkingDirectory = "E:\Documents\DEGOO\CANTINA\sistema_cantina"
oShortcut.IconLocation = "shell32.dll,167"
oShortcut.Description = "Sistema da Cantina Escolar - CISEB Celso Rodrigues"
oShortcut.Save
WScript.Echo "Atalho criado na Area de Trabalho com sucesso!"