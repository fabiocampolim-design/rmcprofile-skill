# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Fabio Campolim
<#
.SYNOPSIS  Register (or -Remove) a weekly Windows Task Scheduler job that runs
           watch_upstream.py --weekly (playbook S8 / rule 23), console appended to
           <study>/forum/upstream-watch/logs/task.log.
.PARAMETER Python   interpreter (default %USERPROFILE%\miniconda3\envs\rmcprofile\python.exe)
.PARAMETER Day      weekday of the trigger (default Monday)
.PARAMETER At       time of the trigger, HH:mm (default 08:00)
.PARAMETER Remove   unregister the task instead
.PARAMETER DryRun   print what would be registered, register nothing
.PARAMETER Version  print the rmcprofile-skill version
Exit 0 ok, 1 failed.
#>
param(
    [string]$Python = "$env:USERPROFILE\miniconda3\envs\rmcprofile\python.exe",
    [string]$Day = "Monday",
    [string]$At = "08:00",
    [switch]$Remove,
    [switch]$DryRun,
    [switch]$Version
)
$ErrorActionPreference = "Stop"
$here = Split-Path -Parent $MyInvocation.MyCommand.Path
if ($Version) { Write-Output ("rmcprofile-skill " + (Get-Content (Join-Path $here "..\VERSION") -Raw).Trim()); exit 0 }
$script = Join-Path $here "watch_upstream.py"
$name = "rmcprofile-skill upstream watch"
# The scheduler discards the console: run through cmd.exe and append both streams to a log
# under the gitignored state directory (playbook: a run that exits 1 must leave a trace).
$logDir = [System.IO.Path]::GetFullPath((Join-Path $here "..\..\forum\upstream-watch\logs"))
$log = Join-Path $logDir "task.log"
$argument = "/c `"`"$Python`" `"$script`" --weekly >> `"$log`" 2>&1`""
if ($DryRun) {
    Write-Output "DRY-RUN: Register-ScheduledTask '$name' weekly $Day $At -> cmd.exe $argument"
    exit 0
}
if ($Remove) {
    Unregister-ScheduledTask -TaskName $name -Confirm:$false
    Write-Output "removed '$name'"
    exit 0
}
if (-not (Test-Path $Python)) { Write-Output "python not found: $Python"; exit 1 }
New-Item -ItemType Directory -Force $logDir | Out-Null
$action = New-ScheduledTaskAction -Execute "cmd.exe" -Argument $argument -WorkingDirectory $here
$trigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek $Day -At $At
$settings = New-ScheduledTaskSettingsSet -StartWhenAvailable -ExecutionTimeLimit (New-TimeSpan -Hours 1)
Register-ScheduledTask -TaskName $name -Action $action -Trigger $trigger -Settings $settings `
    -Description "rmcprofile-skill S8 weekly upstream watch (SourceForge listing, site pages, conda tools, GitHub neighbours, tracker status)" -Force | Out-Null
Write-Output "registered '$name' weekly $Day $At -> $Python (console -> $log)"
