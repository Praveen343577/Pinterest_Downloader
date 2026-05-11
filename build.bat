@echo off
rmdir /s /q build
rmdir /s /q dist

pyinstaller --onefile --name Downloader ^
  --add-binary "resources\gallery-dl.exe;resources" ^
  --hidden-import rich ^
  --hidden-import rich.progress ^
  --hidden-import rich.live ^
  --hidden-import rich.panel ^
  --hidden-import rich.table ^
  --hidden-import rich.text ^
  --hidden-import rich.console ^
  --hidden-import rich.box ^
  src\main.py