import subprocess
import sys
import os
import socket
import urllib.request

task = sys.argv[1]
healthcheck = os.environ.get('CHECKURL_' + task.upper(), None)

def ping(s = ''):
    if healthcheck:
        try:
            urllib.request.urlopen(healthcheck + s, timeout=10)
        except socket.error as e:
            print("Failed to ping healthchecks.io")
            print(e)

ping('/start')
try:
    if task == 'create':
        rclone_destination = os.environ['DESTINATION']
        rclone_args = os.environ.get('RCLONE_ARGS', '--fast-list --delete-after --delete-excluded')
        subprocess.run('borgmatic -p -C -c /mnt/borgmatic -v 1', shell=True, check=True)
        subprocess.run(f'rclone sync /mnt/repo {rclone_destination} --config /mnt/rclone_config/rclone.conf --stats-log-level NOTICE --stats-one-line {rclone_args}', shell=True, check=True)
    elif task == 'check':
        check_options = os.environ.get('CHECK_OPTS', '')
        subprocess.run(f'borg check {check_options} /mnt/repo -v', shell=True, check=True)
    ping()
except subprocess.CalledProcessError as e:
    ping('/fail')
print()
