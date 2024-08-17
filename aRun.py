import subprocess
import os
import signal

scripts = [
    "Bartleby.py",
    "DumbAhhPeople.py",
    "docgen.py",
    "numerade.py",
    "saver.py",
    "scribd.py",
    "StudocuBot.py"
    "QOLchannels.py"
    "trail.py"
]

processes = []

# Start all scripts in new command prompt windows
for script in scripts:
    process = subprocess.Popen(["python", script], creationflags=subprocess.CREATE_NEW_CONSOLE)
    processes.append(process)

while True:
    command = input("Type 'close' to close all tabs or 'exit' to exit the script: ").strip().lower()
    
    if command == 'close':
        # Close all the command prompt windows that were opened
        for process in processes:
            os.kill(process.pid, signal.SIGTERM)
        print("All tabs have been closed.")
        break
    elif command == 'exit':
        print("Exiting without closing tabs.")
        break
    else:
        print("Invalid command. Please type 'close' to close tabs or 'exit' to exit.")