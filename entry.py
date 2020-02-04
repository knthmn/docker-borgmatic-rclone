import os


def run(command):
    """Run the command and return stout as a string"""
    return os.popen(command).read()


env = os.environ

# Set timezone
if 'TZ' not in env:
    print('TZ not set')
    exit(1)
tz = env['TZ']
run(f'cp /usr/share/zoneinfo/{tz} /etc/localtime')
run(f'echo {tz} > /etc/timezone')

# Create user and cache directory
print('Entry script started')
user = 'backup_user'
group = 'backup_group'
if ('UID' in env) != ('GID' in env):
    print('UID and GID must be defined together')
    exit(1)
if 'UID' in env:
    uid = env['UID']
    gid = env['GID']
    q = run(f'getent group {gid}')
    if q == '':
        print(f'Creating group {gid}({group})')
        run(f'addgroup --gid "{gid}" {group}')
    else:
        group = q.split(':')[0]
        print(f'Group {group} already exists')
    q = run(f'getent passwd {uid}')
    if q == '':
        print(f'Creating user {uid}({user})')
        run(f'adduser -D --uid {uid} {user} --ingroup {group}')
    else:
        user = q.split(':')[0]
        print(f'User {user} already exists')
else:
    user = 'root'
    group = 'root'
run_result = run(f'su {user} -c \'id\'')
run(f'mkdir -p /home/{user}/.cache')
run(f'ln -s /borg_cache /home/{user}/.cache/borg')
print(f'User is {run_result}')
print()

# Setup script for creating and uploading archives
if ('DESTINATION' not in env):
    print('DESTINATION not set')
    exit(1)
rclone_destination = env['DESTINATION']
rclone_args = env['RCLONE_ARGS']
healthcheck = 'CHECKURL_CREATE' in env
if healthcheck:
    check_url = env['CHECKURL_CREATE']
script = open('/create.sh', 'w+')
script.write('\n'.join([
    'echo Starting backup as $(id)',
    f'wget {check_url}/start -O /dev/null' if healthcheck else 'true',
    'borgmatic --create --prune --stats -v 1 && \\',
    f'rclone sync /mnt/repo {rclone_destination} --config /rclone_config/rclone.conf -v {rclone_args} && \\',
    f'wget {check_url} -O /dev/null || wget {check_url}/fail -O /dev/null' if healthcheck else 'true',
    'echo Finished backup'
]))
script.close()
print("/create.sh content:")
print(open('/create.sh', 'r').read())
print()

# Setup script for checking archive
healthcheck = 'CHECKURL_CHECK' in env
if healthcheck:
    check_url = env['CHECKURL_CHECK']
script = open('/check.sh', 'w+')
script.write('\n'.join([
    'echo Starting integrity check',
    f'wget {check_url}/start -O /dev/null' if healthcheck else 'true',
    'borg check /mnt/repo && \\',
    f'wget {check_url} -O /dev/null || wget {check_url}/fail -O /dev/null' if healthcheck else 'true',
    'echo Finished integrity check'
]))
script.close()
print("/check.sh content:")
print(open('/check.sh', 'r').read())
print()

# Setup crontab
crontab_file = '/crontab.txt'
crontab = open(crontab_file, 'w+')
if 'CRON_CREATE' in env:
    cron_create = env['CRON_CREATE']
    crontab.write(
        f"{cron_create} /usr/bin/flock lock -c \"su {user} -c '/bin/sh /create.sh'\"\n")
if 'CRON_CHECK'in env:
    cron_check = env['CRON_CHECK']
    crontab.write(
        f"{cron_check} /usr/bin/flock lock -c \"su {user} -c '/bin/sh /check.sh'\"\n")
crontab.close()
print("crontab.txt content:")
print(open(crontab_file, 'r').read())
print()

# Run create archive script once if requested
run_once = bool(int(env['RUN_ONCE']))
if (run_once):
    print("RUN_ONCE set to 1, running once")
    os.system(f"su {user} -c '/bin/sh /create.sh'")

# Start cron
print("Starting schedule")
run('/usr/bin/crontab /crontab.txt')
os.system('/usr/sbin/crond -f')
