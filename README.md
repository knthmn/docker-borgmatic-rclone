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
      - ./.config/borg:/mnt/borg_config:ro
    environment:
      - TZ=${TZ}
      - "DESTINATION=backup_cloud:"
      - "CRON_CREATE=35 * * * *"
      - "CRON_CHECK=36 3 * * *"
```


Volumes:
* `/mnt/source`: used to mount files that need to be backed up
* `/mnt/repo`: borg repository, rclone always uploads this folder
* `/mnt/rclone_config`: directory for rclone config
* `/mnt/borgmatic`: directory for borgmatic yaml files
* `/mnt/borg_cache`: directory for borg cache
* `/mnt/borg_config`: directory for borg config

The container will run the following two cron tasks. Both tasks share a mutex lock so there is at most one task running.
* create and prune: schedule specified by `CRON_CREATE`, which runs `borgmatic create prune` for all the borgmatic configurations, and upload the repo to `DESTINATION` by using `rclone`. 
* check: schedule specified by `CRON_CHECK`, which runs `borgmatic check` on the repo.


The image also has the following features
* A different user for the borg repo can be set using `GID` and `UID`. By default `root:root` is used.
* healthchecks.io can be used to monitor the jobs by setting `CHECKURL_CREATE` and `CHECKURL_CHECK`. 
* The create task can be run at the start of the container by setting `AT_START=1`.
* Arguments for rclone can be changed by `RCLONE_ARGS`, default is `--fast-list --delete-after --delete-excluded`

## Notes
I created this container because it suits my workflow for creating backups. I was originally using both `pfidr34/docker-rclone` and `b3vis/docker-borgmatic`. It bugged me that `b3vis/docker-borgmatic` didn't have the feature to act as another user. I thought it would be a good exercise for me to create my own image.

I used Python for the entry script because I am not comfortable with shell script and it was used by borgmatic anyway. The Alpine package install list was copied from the two images mentioned above.

This is my first image so please be gentle if there is something wrong. The features I added to the image suit my personal use, but I am happy to add any features you want if it is not too complicated.
