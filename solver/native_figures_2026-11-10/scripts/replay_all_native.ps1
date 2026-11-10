$taskRoot='C:\Users\A320N\Documents\ChatGPT\MMME3086 cw1\solver\native_figures_2026-11-10'
New-Item -ItemType Directory -Force (Join-Path $taskRoot 'replay\case03'),(Join-Path $taskRoot 'replay\case05'),(Join-Path $taskRoot 'replay\taskA'),'D:\CFD_WorkScratch\native_figures_2026-11-10\temp' | Out-Null
$env:TEMP='D:\CFD_WorkScratch\native_figures_2026-11-10\temp'
$env:TMP=$env:TEMP
Set-Location -LiteralPath $taskRoot
& 'D:\ANSYS Inc\v222\fluent\ntbin\win64\fluent.exe' 2ddp -t1 -gu -wait -i (Join-Path $taskRoot 'scripts\complete_native_replay.jou')
