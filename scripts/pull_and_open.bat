@echo off
:: Wait for network
ping -n 5 8.8.8.8 > nul
git -C "C:\Users\kevin\logseq" pull
set PYTHONUTF8=1
python "C:\Users\kevin\logseq\scripts\open_today.py"
