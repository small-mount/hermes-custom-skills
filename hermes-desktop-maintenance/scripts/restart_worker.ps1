# Hermes 桌面端干净重启 worker（模板）
# 用法：复制到 workspace\hermes_restart_<日期>\ 后按需改 $root；由 wmic/schtasks 以「脱离进程树」方式启动（见 SKILL.md）
$ErrorActionPreference = 'Continue'
$root = 'C:\Users\da_shan\AppData\Local\hermes\workspace\hermes_restart_20260929'   # <<< 改成当次的目录
$log  = Join-Path $root 'restart.log'
function L($m){ Add-Content -Path $log -Value ('[{0}] {1}' -f (Get-Date -Format 'HH:mm:ss'), $m) -Encoding UTF8 }

L ('worker started; pid=' + $PID + '; parent=' + (Get-CimInstance Win32_Process -Filter ('ProcessId=' + $PID)).ParentProcessId)
Start-Sleep -Seconds 40   # 留给当前回合发完告知消息

L 'wake: killing desktop app family (taskkill /IM Hermes.exe /T /F)'
& taskkill /IM Hermes.exe /T /F *>> $log
Start-Sleep -Seconds 3

# 动态识别网关（勿杀）：python 且 cmdline 含 'gateway run --replace'
$gwp = Get-CimInstance Win32_Process | Where-Object { $_.Name -eq 'python.exe' -and $_.CommandLine -match 'gateway run --replace' } | Select-Object -First 1
$gw = 0
if($gwp){ $gw = [int]$gwp.ProcessId }
L ('gateway pid (spared) = ' + $gw)

function IsUnder([int]$p, [int]$r){
  for($i = 0; $i -lt 12; $i++){
    if($r -gt 0 -and $p -eq $r){ return $true }
    if($p -le 4){ return $false }
    $q = Get-CimInstance Win32_Process -Filter ('ProcessId=' + $p) -ErrorAction SilentlyContinue
    if(-not $q){ return $false }
    $p = [int]$q.ParentProcessId
  }
  return $false
}
$killed = 0; $skipped = 0
Get-CimInstance Win32_Process | Where-Object { $_.Name -eq 'node.exe' -and $_.CommandLine -match 'hermes' } | ForEach-Object {
  $id = [int]$_.ProcessId; $par = [int]$_.ParentProcessId
  if( (IsUnder $id $gw) -or (IsUnder $par $gw) ){
    L ('skip (gateway tree): pid ' + $id); $skipped++
  } else {
    L ('kill node pid ' + $id + ' :: ' + $_.CommandLine.Substring(0, [Math]::Min(110, $_.CommandLine.Length)))
    Stop-Process -Id $id -Force -ErrorAction SilentlyContinue
    $killed++
  }
}
L ('leftover sweep: killed=' + $killed + ' skipped=' + $skipped)
Start-Sleep -Seconds 3

$remain = @(Get-Process -Name Hermes -ErrorAction SilentlyContinue).Count
L ('remaining Hermes.exe: ' + $remain)
$remainN = @(Get-CimInstance Win32_Process | Where-Object { $_.Name -eq 'node.exe' -and $_.CommandLine -match 'hermes' }).Count
L ('remaining hermes-node: ' + $remainN)

L 'relaunching desktop: hermes.exe desktop --skip-build'
Start-Process -FilePath 'C:\Users\da_shan\AppData\Local\hermes\hermes-agent\.hermes\bin\hermes.exe' -ArgumentList 'desktop','--skip-build' -WorkingDirectory 'C:\Users\da_shan\AppData\Local\hermes\hermes-agent' -WindowStyle Minimized
Start-Sleep -Seconds 25
$new = @(Get-Process -Name Hermes -ErrorAction SilentlyContinue).Count
L ('after relaunch Hermes.exe count: ' + $new)
L '== worker done =='
