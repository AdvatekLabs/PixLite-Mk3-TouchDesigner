$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
[System.Environment]::SetEnvironmentVariable('TD_PIXLITE', $ScriptDir, 'User')
$env:TD_PIXLITE = $ScriptDir
Write-Host "TD_PIXLITE set to $ScriptDir"
