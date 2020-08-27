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
print(f'User is {run_result}')

# Check arugments
if ('DESTINATION' not in env):
    print('DESTINATION not set')
    exit(1)

# Setup crontab
crontab_file = '/crontab.txt'
crontab = open(crontab_file, 'w+')
for task in ['create', 'check']:
    cron = env.get('CRON_' + task.upper(), None)
    if (cron):
        crontab.write(f'{cron} /usr/bin/flock lock -c "su {user} -c \'/usr/bin/python3 /script.py {task}\'"\n')
crontab.close()
print("--- crontab.txt content ---")
print(open(crontab_file, 'r').read())

# Run create archive script once if requested
run_once = 'AT_START' in env and int(env['AT_START'])
if (run_once):
    print("AT_START set to 1, now running create task once")
    os.system(f'su {user} -c \'/usr/bin/python3 /script.py create\'')
    print()

# Start cron
print("Starting cron schedule")
run('/usr/bin/crontab /crontab.txt')
os.system('/usr/sbin/crond -f')
