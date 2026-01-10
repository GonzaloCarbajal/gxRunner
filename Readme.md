# GeneXus Launcher

Este proyecto permite gestionar y lanzar diferentes versiones de GeneXus y sus respectivas KBs, facilitando la ejecución de comandos como `/install`.

## Instalación de dependencias

Antes de comenzar, instala PyInstaller para poder generar el ejecutable:

```powershell
py -m pip install pyinstaller
```

## Cerrar procesos activos

```powershell
taskkill /IM GeneXusLauncher.exe /F
```

## Limpiar versiones previas

```powershell
Remove-Item -Path "dist/GeneXusLauncher.exe" -Force
```

## Generar el ejecutable (.exe)

```powershell
py -m PyInstaller --noconsole --onefile --name GeneXusLauncher launcher_gx.py
```


¡Con esto ya tienes el manual de instrucciones perfecto para tu proyecto! 🚀📂