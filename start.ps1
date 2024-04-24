cd C:\Users\I047787\Documents\project\whisper-writer
.venv\Scripts\activate
# Start the whisper server in WSL
Start-Process wsl -ArgumentList "--distribution Ubuntu-22.04 bash -c '/home/roger/projects/whisper.cpp/start-server.sh'" -WindowStyle Hidden
# Start the server in WSL
# add for -WindowStyle to hide window
$env:OPENAI_API_BASE = "http://127.0.0.1:8080/inference"
Start-Process python -ArgumentList "run.py" -WindowStyle Hidden