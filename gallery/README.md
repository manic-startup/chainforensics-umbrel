# Gallery Images

Place your app screenshots here. Recommended specifications:

- **Format:** PNG or JPG
- **Aspect Ratio:** 16:9 recommended
- **Resolution:** 1920x1080 or higher
- **File Size:** Under 500KB each

## Required Screenshots

1. `dashboard.png` - Main dashboard view showing the analysis interface
2. `privacy-score.png` - Privacy scoring results with detailed breakdown
3. `graph-view.png` - Graph visualization of transaction flows

## Hosting

After adding screenshots, upload them to a publicly accessible URL:

1. **GitHub Raw URLs** (recommended for open source):
   ```
   https://raw.githubusercontent.com/chainforensics/chainforensics-umbrel/main/gallery/dashboard.png
   ```

2. **CDN Hosting** (for production):
   Use a reliable CDN service to ensure fast loading

## Update umbrel-app.yml

After hosting images, update the `gallery:` section in `umbrel-app.yml`:

```yaml
gallery:
  - https://your-url.com/dashboard.png
  - https://your-url.com/privacy-score.png
  - https://your-url.com/graph-view.png
```
