' Hidden bat launcher
' Usage: wscript.exe run_hidden.vbs "C:\path\to\target.bat"
' Purpose: Windowsタスクスケジューラから起動されるbatの黒窓を完全に非表示にする
' 0 = SW_HIDE (window not shown), False = don't wait for completion
Set shell = CreateObject("WScript.Shell")
shell.Run """" & WScript.Arguments(0) & """", 0, False
