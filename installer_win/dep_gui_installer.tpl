﻿
[Header]
ProjectFileVersion = 1.1
[General]
Program name = Deposit GUI
Program version = %(version)s
Windows 2000 = 0
Windows XP = 1
Windows Server 2003 = 1
Windows Vista = 1
Windows Server 2008 = 1
Windows 7 = 1
Windows 8 = 1
Windows 10 = 1
Windows Server 2016 = 1
DoNotCheckOS = 1
Company name = Peter Demján
Website = https://github.com/demjanp/deposit_gui
SFA = 0
DFA = 0
Comp = 1
[Graphics]
Wizard image = %(root_path)s\installer_win\dep_installer.jpg
Header image = %(root_path)s\installer_win\dep_icon.jpg
Show Label = 1
VisualStylesEnabled = 1
[Files]
Installation path = <ProgramFiles>\<AppName>\
Autcip = 1
[Uninstall]
Vwau = 0
Website = https://
Include uninstaller = 1
Uninstaller filename = Uninstall
UseCustomDisplayIcon = 0
CustomDisplayIcon = <InstallPath>\
[Licence]
Licence dialog = 0
[Finish]
Sart program = 0
Reboot computer = 0
Program = <InstallPath>\
ProgramArguments = 
[Shortcuts]
Allowtc = 0
Shortcut path = <Company>\<AppName>\
[Serialoptions]
Allows = 0
Number = 1000
Mask = #####-#####-#####-#####
[SplashScreen]
Image = 
Sound = 
Time = 2
PlaySound = 0
Allow = 0
[Build]
File = %(installer_path)s\%(filename)s
SetupIconPath = %(root_path)s\src\deposit_gui\res\deposit_icon.ico
UninstallIconPath = %(root_path)s\src\deposit_gui\res\deposit_icon.ico
CompressionMethod = 0
CompressionLevel = 2
[Updater]
Allow = 0
1 = <AppName>
2 = <AppVersion>
3 = http://
4 = http://
5 = http://
6 = Update
Language = 0
RunProg = 
RunProgs = 0
Execdlls = 0
[Languages]
[Files/Dirs]
%(files)s
[Licence_Begin]
114
{\rtf1\ansi\ansicpg1252\deff0\deflang2057{\fonttbl{\f0\fnil\fcharset0 Arial;}}
\viewkind4\uc1\pard\fs20\par
}
 [Licence_End]
[Registry]
[Variables]
[SCs]
Desktop
Deposit
<InstallPath>\deposit_gui.exe

<InstallPath>\deposit_gui\res\deposit_icon.ico
0
Startmenu
Deposit
<InstallPath>\deposit_gui.exe

<InstallPath>\deposit_gui\res\deposit_icon.ico
0
[IFP_End]
[Serials]
[Serials_End]
[Commands]
