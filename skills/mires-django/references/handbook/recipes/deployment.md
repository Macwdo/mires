# WSGI and ASGI Deployment

## Purpose and when to use it

Choose the server from the connection behavior, not from habit. Gunicorn with
WSGI workers is a strong default for synchronous REST APIs. Daphne with ASGI is
required for the long-lived SSE and WebSocket examples. An integrated project
may send all traffic to Daphne or split REST and realtime traffic into
separately scaled services.

| Concern | Gunicorn and WSGI | Daphne and ASGI |
| --- | --- | --- |
| Synchronous REST | Recommended default | Supported |
| Long-lived SSE | Occupies a worker | Recommended |
| WebSockets | Not supported by WSGI | Supported |
| Scaling unit | Request workers | Connections and event-loop capacity |
| Failure isolation | Simple REST-only process | Can be split from REST |
| Application target | `core.wsgi:application` | `apps.realtime.application:application` |

## When not to use it

Do not place SSE or WebSockets behind synchronous workers, expose development
servers in production, or add a second serving stack without monitoring and
capacity tests. Kubernetes, another process supervisor, or a managed platform
can replace the systemd examples while preserving the same process contracts.

## Responsibilities and invariants

- TLS terminates at a trusted load balancer or reverse proxy.
- Proxy timeouts exceed expected stream duration and buffering is off for SSE.
- WebSocket upgrade headers are forwarded only to the ASGI service.
- Readiness checks verify dependencies; liveness checks only verify the process.
- Workers receive graceful shutdown and enough time to finish or cancel work.
- Secrets live in the runtime environment file, never in service definitions.
- Static assets are served by object storage or a proxy, not Django workers.
- Deployments run migrations as one explicit release step before new workers.

## Complete canonical artifacts

The synchronous profiles and the integrated profile can run REST through
Gunicorn. The service is intentionally independent of a particular cloud.

<!-- artifact: deploy/systemd/generic-api-rest.ini; profiles: base,tasks,storage,vector-ai,full -->
```ini
[Unit]
Description=Generic Django REST API
After=network-online.target
Wants=network-online.target

[Service]
Type=notify
User=django
Group=django
WorkingDirectory=/srv/generic-api/src
EnvironmentFile=/etc/generic-api/environment
ExecStart=/srv/generic-api/.venv/bin/gunicorn --config /srv/generic-api/gunicorn.conf.py core.wsgi:application --bind 127.0.0.1:8000 --workers 3 --worker-tmp-dir /dev/shm --access-logfile - --error-logfile -
ExecReload=/bin/kill -s HUP $MAINPID
KillSignal=SIGTERM
TimeoutStopSec=45
Restart=on-failure
RestartSec=5
PrivateTmp=true
NoNewPrivileges=true

[Install]
WantedBy=multi-user.target
```

The realtime profiles run Daphne. Capacity-test the process count and maximum
connections with production-like message rates.

<!-- artifact: deploy/systemd/generic-api-realtime.ini; profiles: realtime-sse,realtime-channels,realtime,full -->
```ini
[Unit]
Description=Generic Django Realtime API
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=django
Group=django
WorkingDirectory=/srv/generic-api/src
EnvironmentFile=/etc/generic-api/environment
ExecStart=/srv/generic-api/.venv/bin/daphne --bind 127.0.0.1 --port 8001 --proxy-headers core.asgi:application
KillSignal=SIGTERM
TimeoutStopSec=45
Restart=on-failure
RestartSec=5
PrivateTmp=true
NoNewPrivileges=true

[Install]
WantedBy=multi-user.target
```

This proxy configuration sends REST to Gunicorn and only long-lived endpoints
to Daphne. The upstream proxy is also responsible for HTTPS and security
headers in the production environment.

<!-- artifact: deploy/nginx/realtime.conf; profiles: realtime-sse,realtime-channels,realtime,full -->
```text
upstream django_rest {
    server 127.0.0.1:8000;
    keepalive 32;
}

upstream django_realtime {
    server 127.0.0.1:8001;
    keepalive 32;
}

server {
    listen 443 ssl;
    server_name api.example.test;

    ssl_certificate /etc/generic-api/tls/certificate.pem;
    ssl_certificate_key /etc/generic-api/tls/private-key.pem;

    client_max_body_size 2m;

    location /api/v1/events/ {
        proxy_pass http://django_realtime;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto https;
        proxy_buffering off;
        proxy_cache off;
        proxy_read_timeout 1h;
        add_header X-Accel-Buffering no;
    }

    location /ws/ {
        proxy_pass http://django_realtime;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto https;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_read_timeout 1h;
    }

    location / {
        proxy_pass http://django_rest;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto https;
        proxy_connect_timeout 5s;
        proxy_read_timeout 60s;
    }
}
```

## Alternatives and trade-offs

One Daphne service reduces routing complexity and can serve REST, SSE, and
WebSockets together. A split deployment protects ordinary API latency from
large connection counts and permits different scaling, but doubles serving
configuration and health monitoring. Gunicorn can also host an ASGI worker,
but its lifecycle and feature support must be verified against the pinned
versions rather than assumed.

## Required tests

Validate service and proxy syntax, forwarded host and scheme handling, trusted
proxy configuration, graceful termination, migration ordering, readiness and
liveness behavior, static-file routing, body limits, SSE buffering and
heartbeat visibility, WebSocket upgrade and origin rejection, reconnect during
a rolling deployment, and capacity at expected concurrent connection counts.

## Related standards

- [Operations](../docs/operations.md)
- [Security](../docs/security.md)
- [SSE](sse.md)
- [Channels](channels.md)
