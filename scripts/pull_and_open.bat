@echo off
:: Wait for network to be available
ping -n 5 8.8.8.8 > nul
git -C "C:\Users\kevin\logseq" pull
start firefox "file:///C:/Users/kevin/logseq/assets/morning_news_today.html"
