<<<<<<< HEAD
# **Card Issue Service**
## Environment
- docker
- docker-compose

### Notes
- Changes in docker-compose.yml: exposed port, image name, container name
- Changes in supervisord.conf: log files' location

### Use with docker, docker-compose
JUST RUN: `> docker-compose up -d --build`

### Run celery
```celery --app code.tasks worker -Q celery -l DEBUG -c 4```

## Health check
```curl -i http://localhost:5055/v1/voter/common/health_check```

## Container env config:
```/webapps/thecuatui-service/.env```