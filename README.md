# ChainForensics for Umbrel

**Privacy-focused Bitcoin blockchain analysis that runs entirely on your own node.**

## Overview

ChainForensics is a powerful blockchain analysis tool designed for privacy-conscious Bitcoin users. Unlike cloud-based services, all analysis runs locally on your Umbrel node - your addresses and queries never leave your network.

## Features

### 🕵️ KYC Privacy Check
Trace funds backward through the blockchain to find connections to known exchange addresses. Understand your exposure to KYC-linked transactions.

### 🔗 Cluster Detection
Find addresses that are linked together using the Common Input Ownership Heuristic (CIOH). When multiple addresses are spent together, they're provably controlled by the same entity.

### 🏦 Exchange Proximity
Measure how many transaction "hops" separate your address from known exchange wallets. The closer you are, the easier you are to trace.

### 🛡️ UTXO Privacy Rating
Get a privacy score (Red/Yellow/Green) for each UTXO in your wallet based on:
- Exchange distance
- CoinJoin history
- Cluster size
- Age
- Value patterns

### 🔍 Transaction Analysis
Deep dive into any transaction with full input/output breakdown, fee analysis, and flow visualization.

### 📍 Address Lookup
View complete address information including balance, transaction history, and UTXOs.

### 🏷️ Entity Recognition
Identify known wallets, exchanges, and services based on address patterns and transaction behavior.

### 👛 Wallet Fingerprinting
Detect which wallet software likely created a transaction based on input ordering, change detection, and other patterns.

## Requirements

- **Bitcoin Node** - Required for RPC access
- **Fulcrum** - Required for fast address lookups (Electrs also works but is slower)

## Installation

1. Open your Umbrel dashboard
2. Go to App Store → Community Apps
3. Search for "ChainForensics"
4. Click Install

The app will automatically connect to your Bitcoin node and Fulcrum server.

## Usage

After installation, access ChainForensics at:
```
http://umbrel.local:8085
```

Or click the ChainForensics icon in your Umbrel dashboard.

## Privacy Considerations

- **No external connections** - All analysis uses your local node
- **No data collection** - Your queries stay on your network
- **No address leakage** - Unlike block explorers, your addresses aren't sent to third parties
- **Self-sovereign** - You control the analysis tools

## Support

For issues and feature requests, please visit:
https://github.com/chainforensics/umbrel-app/issues

## License

MIT License - See LICENSE file for details.

---

*"Know your chain, protect your privacy."*
