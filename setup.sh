set -e
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3 python3-pip python3-venv ffmpeg git
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
mkdir -p topics episodes src
cp .env.example .env || true
chmod +x src/*.py
echo "\nSetup complete. Edit .env and then run: source venv/bin/activate && python3 src/main_runner.py --once"
