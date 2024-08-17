import subprocess

# Define paths to your Python scripts
scripts = [
    'Coursehero_brainly.py',
    'numerade.py',
    'scribd.py'
]

# Iterate through each script and execute it
for script in scripts:
    # Use subprocess to run each script
    subprocess.run(['python', script], check=True)
