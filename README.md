docker-compose build && docker-compose up -d

docker-compose up -d --build  -d detached mode - no logs

docker-compose down -v  # -v removes volume

docker-compose up -d --force-recreate --no-deps otel-collector
