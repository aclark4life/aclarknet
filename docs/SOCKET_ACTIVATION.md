# Understanding aclarknet.socket - Socket Activation for Django

## What is aclarknet.socket?

`aclarknet.socket` is a **systemd socket unit file** that implements **socket activation** for the aclarknet Django/Wagtail application running on Gunicorn.

## Purpose

The socket file serves three main purposes:

1. **Creates a Communication Channel**: Establishes a Unix domain socket at `/run/gunicorn/aclarknet.sock` that nginx uses to communicate with Gunicorn
2. **Enables Socket Activation**: Allows systemd to manage the socket lifecycle independently from the main application service
3. **Improves Reliability**: Provides graceful restarts and on-demand service activation

## How It Works

### The Request Flow

```
Client (Browser)
    ↓
nginx (Port 443/80)
    ↓
Unix Socket (/run/gunicorn/aclarknet.sock) ← managed by aclarknet.socket
    ↓
Gunicorn (WSGI Server) ← managed by aclarknet.service
    ↓
Django/Wagtail Application
    ↓
MongoDB Database
```

### Socket Activation Pattern

1. **System Boot**: 
   - systemd creates the Unix socket and starts listening
   - The main application service (`aclarknet.service`) may not start yet

2. **First Request**:
   - nginx sends a request to the socket
   - systemd automatically starts `aclarknet.service` if it's not running
   - Once Gunicorn is ready, the request is processed

3. **Subsequent Requests**:
   - Requests flow through the socket to the already-running Gunicorn process
   - No startup delay

4. **Service Restart**:
   - When restarting `aclarknet.service`, the socket remains open
   - Incoming requests queue at the socket
   - Once the service restarts, queued requests are processed
   - **Result**: No dropped connections during deployments

## Configuration Details

```ini
[Socket]
ListenStream=/run/gunicorn/aclarknet.sock  # Unix socket location
RuntimeDirectory=gunicorn                   # Creates /run/gunicorn directory
RuntimeDirectoryMode=0755                   # Directory permissions: rwxr-xr-x
SocketUser=nginx                            # Socket owned by nginx
SocketGroup=nginx                           # Socket group is nginx
SocketMode=0660                             # Permissions: rw-rw----
```

### Permissions Explained

- **RuntimeDirectory=gunicorn**: systemd automatically creates `/run/gunicorn` directory when the socket unit starts
- **RuntimeDirectoryMode=0755**: The directory has read/write/execute for owner, read/execute for group and others
- **SocketUser=nginx**: The socket file is owned by the nginx user
- **SocketGroup=nginx**: The socket file is in the nginx group (Gunicorn also runs as nginx user)
- **SocketMode=0660**: Read/write permissions for both owner and group, enabling bidirectional communication:
  - nginx writes requests to the socket and reads responses
  - Gunicorn reads requests from the socket and writes responses back
  - No access for other users (security)

## Why We Need This File

### Required for Production Deployment

- ✅ **Yes, this file is necessary** for the production deployment as configured
- The `aclarknet.service` explicitly requires it: `Requires=aclarknet.socket`
- nginx configuration expects to proxy requests to this Unix socket
- Removing it would break the production deployment

### Benefits Over Direct TCP Binding

Compared to binding Gunicorn directly to a TCP port:

1. **Security**: Unix sockets are local-only, cannot be accessed remotely
2. **Performance**: Unix sockets are faster than TCP for local communication
3. **Permissions**: File system permissions control access (only nginx can connect)
4. **Zero-Downtime Deploys**: Socket activation enables graceful restarts

## Related Files

### aclarknet.service

The main systemd service file that runs Gunicorn. It:
- Requires `aclarknet.socket` (line: `Requires=aclarknet.socket`)
- Binds Gunicorn to the same socket path: `--bind unix:/run/gunicorn/aclarknet.sock`

### nginx-aclarknet.conf

nginx configuration that proxies requests to the socket:
```nginx
upstream aclarknet {
    server unix:/run/gunicorn/aclarknet.sock fail_timeout=0;
}
```

### deploy.sh

Deployment script that:
- Copies `aclarknet.socket` to `/etc/systemd/system/`
- Enables the socket with `systemctl enable aclarknet.socket`
- Restarts it during deployments

## Common Commands

```bash
# Check socket status
sudo systemctl status aclarknet.socket

# Restart the socket (rarely needed)
sudo systemctl restart aclarknet.socket

# Enable socket to start on boot
sudo systemctl enable aclarknet.socket

# View socket file details
sudo ls -la /run/gunicorn/aclarknet.sock

# Check what's listening on the socket
sudo lsof /run/gunicorn/aclarknet.sock
```

## Troubleshooting

### Socket Permission Errors

If you see permission denied errors:

```bash
# Verify socket ownership
sudo ls -la /run/gunicorn/aclarknet.sock
# Should show: srw-rw---- 1 nginx nginx

# If permissions are wrong, restart the socket
sudo systemctl restart aclarknet.socket
```

### Socket Not Created

If the socket file doesn't exist:

```bash
# Check socket service status
sudo systemctl status aclarknet.socket

# View socket logs
sudo journalctl -u aclarknet.socket -n 50

# The socket unit should automatically create /run/gunicorn
# If it doesn't exist after starting the socket, check logs for errors
sudo systemctl restart aclarknet.socket
sudo ls -la /run/gunicorn/

# Manual directory creation should not be necessary with RuntimeDirectory
# but if needed for troubleshooting:
sudo mkdir -p /run/gunicorn
sudo chown nginx:nginx /run/gunicorn
sudo systemctl restart aclarknet.socket
```

### 502 Bad Gateway

If nginx shows 502 Bad Gateway errors:

1. Socket exists but service isn't running:
   ```bash
   sudo systemctl restart aclarknet.service
   ```

2. Socket doesn't exist:
   ```bash
   sudo systemctl restart aclarknet.socket
   ```

3. Permission issues:
   ```bash
   sudo chown nginx:nginx /run/gunicorn/aclarknet.sock
   sudo chmod 660 /run/gunicorn/aclarknet.sock
   ```

## Alternative Approaches

### Without Socket Activation

If you didn't use socket activation, you would:

1. Bind Gunicorn directly to a port (e.g., 8000)
2. Configure nginx to proxy to `http://localhost:8000`
3. Lose the benefits of socket activation (graceful restarts, automatic starting)

### Example without socket:

```ini
# In aclarknet.service (without socket activation)
ExecStart=/srv/aclarknet/.venv/bin/gunicorn \
          --bind 127.0.0.1:8000 \
          aclarknet.wsgi:application
```

However, the current socket-based approach is **recommended** for production Django applications.

## Resources

- [systemd Socket Activation](https://www.freedesktop.org/software/systemd/man/systemd.socket.html)
- [Gunicorn Unix Socket Configuration](https://docs.gunicorn.org/en/stable/deploy.html)
- [Django Deployment with Gunicorn](https://docs.djangoproject.com/en/stable/howto/deployment/wsgi/gunicorn/)
- [systemd for Administrators (Blog Series)](https://www.freedesktop.org/wiki/Software/systemd/)

## Summary

**Keep this file!** It's an essential part of the production deployment configuration that:
- Enables reliable, production-grade service management
- Provides zero-downtime deployments
- Improves security through Unix socket permissions
- Is required by the current `aclarknet.service` configuration
