#!/bin/bash
set -e  # exit if any command fails

# --- CONFIG ---
PYTHON_VERSION=3.13        # adjust to your preferred version
VENV_NAME=".venv"          # name of the virtual environment
SESSION_NAME="myapp"       # tmux session name
REQUIREMENTS="requirements.txt"
MAIN_SCRIPT="main.py"

# --- 1. Update & install base packages ---
sudo apt update
sudo apt install -y python${PYTHON_VERSION} python${PYTHON_VERSION}-venv python3-pip tmux

# --- 2. Create virtual environment ---
cd app
python${PYTHON_VERSION} -m venv $VENV_NAME

# --- 3. Activate & install dependencies ---
source $VENV_NAME/bin/activate
pip install --upgrade pip
if [ -f "$REQUIREMENTS" ]; then
    pip install -r $REQUIREMENTS
fi
deactivate

# --- 4. Launch in tmux ---
# Kill old session if exists
tmux has-session -t $SESSION_NAME 2>/dev/null && tmux kill-session -t $SESSION_NAME

# Create new tmux session and run script in venv
tmux new-session -d -s $SESSION_NAME "source $VENV_NAME/bin/activate && python $MAIN_SCRIPT"

echo "✅ Environment setup complete." 
echo "💡 Your app is running in tmux session: $SESSION_NAME" 
echo "To attach: tmux attach -t $SESSION_NAME\n" > tmux_session.txt
