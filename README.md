# ChainForensics for Umbrel

Privacy-focused Bitcoin blockchain analysis platform designed for Umbrel nodes.

## Version

**v1.2.0** - Phase 1 MVP Release

## Features

### Core Analysis Tools
- **Transaction Analysis** - Deep inspection of Bitcoin transactions
- **UTXO Tracing** - Follow UTXOs through the blockchain
- **KYC Privacy Checking** - Analyze privacy of exchange withdrawals
- **Cluster Detection** - Advanced Union-Find algorithm for address clustering
- **Exchange Proximity** - Detect connections to 100+ exchange addresses

### Advanced Features (Phase 1 MVP)
- **Entity Recognition** - Identify known wallets and services
- **Risk Intelligence** - Threat level assessment with categorized risks
- **Timestamps** - Full temporal tracking of traced transactions
- **Prioritized Recommendations** - Actionable privacy improvement suggestions
- **Label Manager** - Organize addresses with custom labels and categories
- **Enhanced Privacy Rating** - 7 commercial-grade heuristics for UTXO privacy scoring

### CoinJoin Detection
- Whirlpool (Samourai Wallet)
- Wasabi Wallet
- JoinMarket
- Generic CoinJoin pattern recognition

## Requirements

- **Umbrel OS** - Any recent version
- **Bitcoin Node** - Must be installed and synced
- **Fulcrum** (Optional) - Recommended for enhanced performance

## Installation

### Method 1: Umbrel App Store (Recommended)

1. Open Umbrel dashboard
2. Navigate to App Store
3. Search for "ChainForensics"
4. Click "Install"

### Method 2: Manual Installation

1. SSH into your Umbrel node
2. Clone this repository:
   ```bash
   cd ~/umbrel/app-data
   git clone https://github.com/chainforensics/chainforensics-umbrel.git chainforensics
   ```
3. Install via Umbrel CLI:
   ```bash
   umbrel app install chainforensics
   ```

## Configuration

ChainForensics automatically connects to your Umbrel Bitcoin node. No additional configuration required.

### Optional: Fulcrum Integration

If you have Fulcrum installed on Umbrel, ChainForensics will automatically detect and use it for enhanced blockchain queries.

## Usage

1. Open ChainForensics from your Umbrel dashboard
2. Wait for the Bitcoin node connection to establish (green indicator)
3. Select a tool from the sidebar
4. Enter Bitcoin addresses, transaction IDs, or other required data
5. View detailed privacy analysis results

## Data Storage

All data is stored persistently in your Umbrel app-data directory:
```
~/umbrel/app-data/chainforensics/data/
```

This includes:
- SQLite database with address labels
- Analysis cache
- Application logs

## Privacy & Security

- **No external connections** - All analysis is done locally on your node
- **No data collection** - Your queries never leave your device
- **Open source** - Full code transparency
- **No authentication required** - Designed for personal use on trusted networks

## Support

- **Issues**: https://github.com/chainforensics/chainforensics-umbrel/issues
- **Documentation**: See APP_GUIDE.md in the app directory
- **Community**: Umbrel Community Forum

## License

See LICENSE file for details.

## Changelog

### v1.2.0 (2026-01-01)
- Entity recognition with known wallet identification
- Risk intelligence with threat level assessment
- Timestamps for all traced transactions
- Prioritized recommendations for privacy improvement
- Label Manager tool with full CRUD operations
- Advanced cluster analysis using Union-Find algorithm
- Enhanced UTXO privacy rating with 7 commercial-grade heuristics
- Exchange proximity analysis with 100+ exchange addresses
- All Phase 1 MVP UI improvements and tooltips

### v1.0.0
- Initial Umbrel release
- Transaction analysis
- UTXO tracing
- CoinJoin detection
- KYC privacy checking
- Basic cluster detection
