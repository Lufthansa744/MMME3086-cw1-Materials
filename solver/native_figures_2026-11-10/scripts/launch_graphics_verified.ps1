$env:TEMP='D:\CFD_WorkScratch\native_figures_2026-11-10\temp'
$env:TMP=$env:TEMP
Set-Location -LiteralPath 'C:\Users\A320N\Documents\ChatGPT\MMME3086 cw1\solver\native_figures_2026-11-10'
& 'D:\ANSYS Inc\v222\fluent\ntbin\win64\fluent.exe' 2ddp -t1 -gu -wait
