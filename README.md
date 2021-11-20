** I switched to using [restic](https://restic.readthedocs.io/) so this repository is archived **

# borgmatic with rclone container
![build size](https://img.shields.io/docker/image-size/knthmn/borgmatic-rclone)
![license](https://img.shields.io/github/license/knthmn/docker-borgmatic-rclone)


Image combining [`borgmatic`](https://torsion.org/borgmatic/) and [`rclone`](https://rclone.org/) for periodically creating backup and uploading it to a cloud storage. Get it [here](https://hub.docker.com/r/knthmn/borgmatic-rclone).

## Usage
Here is a minimal `docker-compose.yaml` to backup `./source` and upload it to `backup_cloud:`
```yaml
version: '3'
services:
  borgmatic-rclone:
    image: knthmn/borgmatic-rclone
    container_name: backup-history
    network_mode: bridge
    volumes:
      - ./source:/mnt/source:ro
      - ./repo:/mnt/repo
      - ./.config/rclone:/mnt/rclone_config:ro
      - ./.config/borgmatic:/mnt/borgmatic:ro
      - ./.cache/borg:/mnt/borg_cache
      - ./.config/borg:/mnt/borg_config
    environment:
      - TZ=${TZ}
      - "DESTINATION=backup_cloud:"
      - "CRON_CREATE=35 * * * *"
      - "CRON_CHECK=36 3 * * *"
```


Volumes:
* `/mnt/source`: used to mount files that need to be backed up. Should be mounted read-only.
* `/mnt/repo`: borg repository, rclone always uploads this folder. Remember to have `location/repositories` in the borgmatic config point here.
* `/mnt/rclone_config`: directory for rclone config. Read-only.
* `/mnt/borgmatic`: directory for borgmatic yaml files. Read-only.
* `/mnt/borg_cache`: directory for borg cache. Must be writable.
* `/mnt/borg_config`: directory for borg config. Must be writable for rclone to save the latest state and keys of the repo.

The container will run the following two cron tasks. Both tasks share a mutex lock so there is at most one task running.
* create: schedule specified by `CRON_CREATE`, which runs `borgmatic` on the borgmatic configurations, and upload the repo to `DESTINATION` by using `rclone`.
* check: schedule specified by `CRON_CHECK`, which runs `borg check {CHECK_OPTS}` on the repo. This task can be used to run a more time consuming check task and can be disabled by not specifying `CRON_CHECK`


The image also has the following features
* A different user for the borg repo can be set using `GID` and `UID`. By default `root:root` is used.
* healthchecks.io can be used to monitor the jobs by setting `CHECKURL_CREATE` and `CHECKURL_CHECK`. 
* The create task can be run at the start of the container by setting `AT_START=1`.
* Arguments for rclone can be changed by `RCLONE_ARGS`, default is `--fast-list --delete-after --delete-excluded`
* Arguments for the check task can be changed by `CHECK_OPTS`, default is empty.

## Notes
I created this container because it suits my workflow for creating backups. I was originally using both `pfidr34/docker-rclone` and `b3vis/docker-borgmatic`. But I figured that it would be easier to have a single image.

The features I added to the image are for my personal use, but I am happy to add any features you want if it is not too complicated.
