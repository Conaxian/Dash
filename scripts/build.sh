temp=$(realpath "$0")
path=$(dirname "$temp")

python -m PyInstaller --onefile --windowed \
--workpath=$path/../build --distpath=$path/../dist --specpath=$path/../build \
--name="Dash" --icon=$path/../resources/icon.ico $path/../dash/main.py
