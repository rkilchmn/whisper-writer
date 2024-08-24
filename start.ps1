cd C:\Users\I047787\Documents\project\whisper-writer
.venv\Scripts\activate
# Start the whisper server in WSL
# Start-Process wsl -ArgumentList "--distribution Ubuntu-22.04 bash -c '/home/roger/projects/whisper.cpp/start-server.sh'" -WindowStyle Hidden

# start remote-faster-whisper container
# Start-Process wsl -ArgumentList "--distribution Ubuntu-22.04 bash -c '/home/roger/projects/remote-faster-whisper/docker-run.sh'" -WindowStyle Hidden

# Start the WSL distribution with dbus-launch, remote-faster-whisper container will be started as it runs until stopped
wsl.exe --distribution Ubuntu-22.04 --exec dbus-launch true

# start python program
# use local whisper API compatible with openai
$env:OPENAI_API_BASE = "http://127.0.0.1:8080/inference"
Start-Process python -ArgumentList "run.py" -WindowStyle Hidden