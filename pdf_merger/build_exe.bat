@echo off
REM Construit dist\PDFMerger.exe (a lancer depuis le dossier DataScience-Projects)
python -m pip install --upgrade pypdf tkinterdnd2 pyinstaller || goto :error
python -m PyInstaller --noconfirm --onefile --windowed --name PDFMerger ^
    --collect-all tkinterdnd2 pdf_merger\launcher.py || goto :error
echo.
echo OK : dist\PDFMerger.exe
goto :eof
:error
echo La construction a echoue.
exit /b 1
