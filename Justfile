set shell := ["pwsh.exe", "-c"]

build: build-package-manager build-cpython

build-package-manager:
    Set-Location package-manager; cargo build --release -j 12
    @New-Item -ItemType Directory -Force -Path G:\Dx\bin | Out-Null
    @Copy-Item package-manager\target\release\*.exe G:\Dx\bin\ -Force -ErrorAction SilentlyContinue

build-cpython:
    Set-Location cpython\PCbuild; cmd.exe /c build.bat -p x64 | Out-Null
    @New-Item -ItemType Directory -Force -Path G:\Dx\bin | Out-Null
    @Copy-Item cpython\PCbuild\amd64\*.exe G:\Dx\bin\ -Force -ErrorAction SilentlyContinue
    @New-Item -ItemType Directory -Force -Path G:\Dx\bin | Out-Null
    @Copy-Item cpython\PCbuild\amd64\*.dll G:\Dx\bin\ -Force -ErrorAction SilentlyContinue



