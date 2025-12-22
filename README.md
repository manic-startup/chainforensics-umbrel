# ChainForensics Umbrel Community App Store v1.2.0

This is a community app store for Umbrel containing ChainForensics - a privacy-focused Bitcoin blockchain analysis tool.

## 🚀 How to Install

### Step 1: Add this Community App Store to your Umbrel

1. Open your Umbrel dashboard
2. Go to **App Store**
3. Click the **⋮** (three dots) menu in the top-right corner
4. Select **"Community App Stores"**
5. Enter this URL:
   ```
   https://github.com/manic-startup/chainforensics-umbrel
   ```
6. Click **"Add"**

### Step 2: Install ChainForensics

1. Go back to the **App Store**
2. You'll see a new section for this community store
3. Find **ChainForensics** and click **Install**

That's it! The app will automatically connect to your Bitcoin Node and Electrs (if installed).

---

## 📋 Requirements

| Requirement | Status | Notes |
|-------------|--------|-------|
| **Bitcoin Node** | Required | Must be fully synced |
| **txindex=1** | Required | Transaction indexing must be enabled |
| **Electrs** | Recommended | Enables address lookups and forward tracing |

### Enabling txindex (if not already enabled)

If you installed Bitcoin Node after syncing, you may need to enable txindex:

1. SSH into your Umbrel: `ssh umbrel@umbrel.local`
2. Edit the config:
   ```bash
   nano ~/umbrel/app-data/bitcoin/data/bitcoin/bitcoin.conf
   ```
3. Add this line: `txindex=1`
4. Save and exit (Ctrl+X, Y, Enter)
5. Restart Bitcoin Node from the Umbrel dashboard
6. Wait for reindexing (can take several hours)

---

## 🔒 Privacy & Security

- ✅ **100% Local** - All analysis runs on YOUR node
- ✅ **No External Servers** - No data leaves your network
- ✅ **No Tracking** - Your queries are completely private
- ✅ **Open Source** - Full code transparency

---

## ✨ Features

- **Transaction Analysis** - Examine any transaction's inputs, outputs, and fees
- **UTXO Tracing** - Follow the money trail forward or backward
- **CoinJoin Detection** - Identify Whirlpool, Wasabi, and JoinMarket transactions
- **Privacy Scoring** - Rate how private your UTXOs are
- **KYC Privacy Check** - See if your exchange withdrawal is traceable
- **Dust Attack Detection** - Find suspicious tracking UTXOs
- **Address Lookup** - Check balances and UTXOs for any address

---

## 🛠️ Troubleshooting

### "Transaction not found" error
- Ensure `txindex=1` is enabled in Bitcoin Core
- Wait for reindexing to complete

### Electrs features not working
- Install Electrs from the official Umbrel App Store
- Wait for Electrs to fully sync (can take several hours)

### App won't start
- Check that Bitcoin Node is running and synced
- View logs: Go to the app → Settings → View Logs

---

## 📚 Documentation

See [APP_GUIDE.md](./chainforensics-app/APP_GUIDE.md) for detailed usage instructions.

---

## 🍺 Support Development

If you find this useful, consider buying me a drink! Bitcoin address is available in the app.

---

## 📄 License

GNU Affero General Public License v3.0
