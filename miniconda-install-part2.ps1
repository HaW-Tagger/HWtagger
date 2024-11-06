Invoke-Conda init

Invoke-Conda config --set auto_activate_base false

Invoke-Conda env create --file .\environments.yml

Invoke-Conda activate hwtagger-cudnn
Write-Output "Launching HW Tagger"
& "python" 'pyside6_ui.py'

Pause