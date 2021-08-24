# Upcoming
 - Bumped versions borg to 1.1.17, borgmatic to 1.5.18, rclone to 1.53.3
 - borgbackup is now installed from pip
 - ca-certificates is added to image
 - `(generate|upgrade|validate)-borgmatic-config` commands can now be accesed in the container


# 2021.02.19
`/mnt/borgmatic` is now soft linked to `/etc/borgmatic.d`. User can now execute `borgmatic` in the container without specifying the path of the configuration file.
