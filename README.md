# ChainForensics - Umbrel App

This folder contains the Umbrel App Store compatible version of ChainForensics.

## Folder Structure

```
ChainForensics-umbrel/
├── umbrel-app.yml          # App manifest (required)
├── docker-compose.yml      # Docker services definition (required)
├── exports.sh              # Environment variable exports (required)
├── icon.svg                # App icon (required, 512x512 recommended)
├── README.md               # This file
├── backend/
│   └── Dockerfile          # API server container
└── frontend/
    ├── Dockerfile          # Web UI container
    └── nginx.conf          # Nginx proxy configuration
```

## Pre-Submission Checklist

Before submitting to the Umbrel App Store:

### 1. Build and Push Docker Images

```bash
# Build images
docker build -t chainforensics/chainforensics-api:v3.1.0 ./backend
docker build -t chainforensics/chainforensics-web:v3.1.0 ./frontend

# Push to Docker Hub
docker push chainforensics/chainforensics-api:v3.1.0
docker push chainforensics/chainforensics-web:v3.1.0
```

### 2. Update docker-compose.yml with Image Digests

After pushing, get the SHA256 digests:

```bash
docker inspect --format='{{index .RepoDigests 0}}' chainforensics/chainforensics-api:v3.1.0
docker inspect --format='{{index .RepoDigests 0}}' chainforensics/chainforensics-web:v3.1.0
```

Replace `@sha256:placeholder` in docker-compose.yml with actual digests.

### 3. Host Assets

Upload the following to a public URL (GitHub raw or CDN):
- `icon.svg` - App icon
- Gallery screenshots (PNG/JPG, 16:9 aspect ratio recommended)

Update URLs in `umbrel-app.yml`:
- `icon:` field
- `gallery:` array

### 4. Validate Manifest

Ensure all required fields are present:
- [x] manifestVersion: 1.1
- [x] id: chainforensics
- [x] name: ChainForensics
- [x] tagline: (under 50 chars recommended)
- [x] icon: (valid SVG URL)
- [x] category: bitcoin
- [x] version: (semantic versioning)
- [x] port: 8089
- [x] description: (multi-line description)
- [x] developer: ChainForensics
- [x] website: (valid URL)
- [x] repo: (GitHub URL)
- [x] support: (issues URL)
- [x] gallery: (array of image URLs)
- [x] dependencies: [bitcoin]

### 5. Test Locally on Umbrel

```bash
# Copy to Umbrel's app-data directory
scp -r ChainForensics-umbrel umbrel@umbrel.local:~/umbrel/app-data/chainforensics

# Or use Umbrel's developer mode
```

### 6. Submit Pull Request

1. Fork https://github.com/getumbrel/umbrel-apps
2. Add your app folder as `chainforensics/`
3. Submit PR with:
   - Clear description of the app
   - Screenshot(s) of working installation
   - Confirmation that you tested on real Umbrel hardware

## Environment Variables

The following environment variables are provided by Umbrel:

| Variable | Description |
|----------|-------------|
| `APP_DATA_DIR` | Persistent storage path for app data |
| `APP_BITCOIN_NODE_IP` | Bitcoin Core container IP |
| `APP_BITCOIN_RPC_USER` | Bitcoin RPC username |
| `APP_BITCOIN_RPC_PASS` | Bitcoin RPC password |

Custom variables defined in `exports.sh`:

| Variable | Description |
|----------|-------------|
| `APP_CHAINFORENSICS_API_IP` | Internal IP for API container |
| `APP_CHAINFORENSICS_WEB_IP` | Internal IP for web container |
| `APP_CHAINFORENSICS_WEB_PORT` | External port (8089) |
| `APP_FULCRUM_HOST` | Optional Fulcrum host IP |
| `APP_FULCRUM_PORT` | Optional Fulcrum port (50001) |

## Dependencies

- **Bitcoin Core** (required) - Must be installed and synced on Umbrel
- **Fulcrum** (optional) - Recommended for enhanced address lookups

## Network Configuration

- API container: Internal only (no external port)
- Web container: Exposed on port 8089
- Both containers use Umbrel's internal network

## Troubleshooting

### App won't start
1. Check Bitcoin Core is running and synced
2. Verify `txindex=1` is enabled in Bitcoin settings

### API connection errors
1. Check container logs: `docker logs chainforensics_api_1`
2. Verify Bitcoin RPC credentials are correct

### Fulcrum features unavailable
1. Install Fulcrum from Umbrel App Store
2. Update `APP_FULCRUM_HOST` and `APP_FULCRUM_PORT` in exports.sh

## License

AGPL-3.0 - See LICENSE in main repository
