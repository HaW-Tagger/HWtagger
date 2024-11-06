if (Get-Command -Name "Invoke-Conda" -ErrorAction SilentlyContinue) {
Start-Process -FilePath "powershell.exe" -ArgumentList "-File .\miniconda-install-part2.ps1"
Write-Output "Conda is already installed on this machine"
} else {
Invoke-WebRequest 'https://repo.anaconda.com/miniconda/Miniconda3-latest-Windows-x86_64.exe' -OutFile "Miniconda3-latest-Windows-x86_64.exe"
$minidir="$Env:UserProfile\miniconda3"
Write-Output "Currently installing Miniconda"
Start-Process "Miniconda3-latest-Windows-x86_64.exe" -Wait -ArgumentList @('/S', '/InstallationType=JustMe', '/RegisterPython=0', '/D="$minidir"')
Remove-Item "Miniconda3-latest-Windows-x86_64.exe"
Start-Process -FilePath "powershell.exe" -ArgumentList "-File .\miniconda-install-part2.ps1"
Write-Output "Miniconda is now installed on this machine"
}