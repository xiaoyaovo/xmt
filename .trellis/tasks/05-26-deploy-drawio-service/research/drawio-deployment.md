# draw.io Deployment Research

## Recommended Approach

Use the official diagrams.net Docker image:

```bash
docker run -d \
  --name drawio \
  --restart unless-stopped \
  -p 127.0.0.1:8081:8080 \
  jgraph/drawio
```

Expose it with an HTTPS reverse proxy:

```nginx
server {
  server_name drawio.example.com;

  location / {
    proxy_pass http://127.0.0.1:8081;
    proxy_http_version 1.1;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
  }
}
```

Then issue TLS with the server's existing certificate workflow, for example:

```bash
certbot --nginx -d drawio.example.com
```

## Embed URLs

Standard diagram embed:

```text
https://drawio.example.com/?embed=1&proto=json&spin=1&ui=min&libraries=1&saveAndExit=0&noSaveBtn=0&noExitBtn=1
```

Whiteboard-style embed:

```text
https://drawio.example.com/?embed=1&proto=json&spin=1&ui=sketch&sketch=1&libraries=1&saveAndExit=0&noSaveBtn=0&noExitBtn=1
```

## Rollback

```bash
docker rm -f drawio
rm -f /etc/nginx/conf.d/drawio.conf
nginx -t && systemctl reload nginx
```

## Current Blocker

Resolved: public key authentication now works for the server alias:

```text
Host sg
  HostName 152.42.201.71
  User root
  Port 22
```

## Actual Deployment

Server:

```text
Ubuntu 24.04.3 LTS
Docker 29.4.0
Docker Compose v5.1.2
Caddy v2.11.2
```

Compose file:

```text
/opt/drawio/docker-compose.yml
```

Container:

```text
drawio  jgraph/drawio:latest  127.0.0.1:8090->8080/tcp
```

Tomcat context override:

```text
/opt/drawio/server.xml
```

The default image mounts the draw.io webapp at root (`path="/" docBase="draw"`). For `https://cxmjtt.com/drawio/`, this was changed to `path="/drawio" docBase="draw"` and mounted into the container read-only.

Caddy routes:

```caddyfile
cxmjtt.com {
    @drawio path /drawio /drawio/*
    handle @drawio {
        reverse_proxy 127.0.0.1:8090
    }

    reverse_proxy 127.0.0.1:3080
}

drawio.cxmjtt.com {
    @root path /
    redir @root /drawio/?lang=zh&ui=min&libraries=1 308

    @drawioRoot path /drawio
    redir @drawioRoot /drawio/ 308

    reverse_proxy 127.0.0.1:8090
}
```

Public working URLs:

- `https://drawio.cxmjtt.com/drawio/?embed=1&proto=json&ui=min&lang=zh`
- `https://drawio.cxmjtt.com/drawio/?embed=1&proto=json&ui=sketch&sketch=1&lang=zh`
- `https://drawio.cxmjtt.com/drawio/?ui=min&lang=zh&libraries=1` for direct manual verification.

Troubleshooting note:

- Do not use `handle_path /drawio/*` with the default root Tomcat context. It strips the prefix, and draw.io later mixes absolute and relative static paths. The visible symptom is an editor shell with missing shape libraries / canvas initialization.
- `embed=1&proto=json` is not a standalone editor test mode. In embed mode the parent page must send the initial XML via `postMessage({ action: "load", xml })`.

DNS / TLS:

- `drawio.cxmjtt.com` resolves to `152.42.201.71`.
- Caddy obtained a Let's Encrypt certificate for `drawio.cxmjtt.com`.
