#!/bin/bash

# ChainForensics - Umbrel Environment Variables
# These are automatically sourced by Umbrel

# App identification
export APP_CHAINFORENSICS_API_IP="10.21.21.150"
export APP_CHAINFORENSICS_WEB_IP="10.21.21.151"
export APP_CHAINFORENSICS_WEB_PORT="8085"

# Network
export APP_NETWORK="umbrel_main_network"

# Bitcoin Core connection (auto-populated by Umbrel)
export APP_BITCOIN_NODE_IP="${APP_BITCOIN_NODE_IP:-10.21.21.8}"
export APP_BITCOIN_RPC_USER="${BITCOIN_RPC_USER:-umbrel}"
export APP_BITCOIN_RPC_PASS="${BITCOIN_RPC_PASS:-}"

# Fulcrum connection (auto-populated by Umbrel)
export APP_FULCRUM_IP="${APP_FULCRUM_IP:-10.21.21.27}"

# Data directory
export APP_DATA_DIR="${EXPORTS_APP_DIR:-$(dirname "${BASH_SOURCE[0]}")}"
