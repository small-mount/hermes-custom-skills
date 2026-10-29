@echo off
rem edge-control skill - 手动以 "Profile 1" 启动受控 Edge（CDP 9222）
rem 前置：先关闭全部 Edge（junction 直启必 err32 否则）。
rem 用法: edge_start.cmd [URL...]
rem 等价于 relay-evaluation-suite/scripts/launch_edge_profile1.cmd（本 skill 为统一入口）。
start "" "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe" --remote-debugging-port=9222 --user-data-dir="C:\Users\da_shan\.openclaw\tools\xbrowser\profiles\edge" --no-first-run --no-default-browser-check --profile-directory="Profile 1" %*
