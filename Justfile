set shell := ["pwsh.exe", "-c"]

build:
    Set-Location package-manager; cargo build --release -j 12
    Copy-Item package-manager\target\release\*.exe G:\Dx\bin\ -Force -ErrorAction SilentlyContinue
