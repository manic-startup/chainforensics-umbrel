#!/bin/bash

# ChainForensics Umbrel App - Environment Exports
# This file is sourced by Umbrel to set up environment variables

# App network configuration
export APP_CHAINFORENSICS_API_IP="10.21.21.50"
export APP_CHAINFORENSICS_WEB_IP="10.21.21.51"
export APP_CHAINFORENSICS_WEB_PORT="8089"

# Bitcoin Core RPC credentials from Umbrel's Bitcoin app
export APP_BITCOIN_NODE_IP="${APP_BITCOIN_NODE_IP:-$BITCOIN_IP}"
export APP_BITCOIN_RPC_USER="umbrel"
export APP_BITCOIN_RPC_PASS="${BITCOIN_RPC_PASS:-}"

# Fulcrum configuration (optional - only if Fulcrum app is installed)
# Users can set these manually if they have Fulcrum installed
export APP_FULCRUM_HOST="${APP_FULCRUM_HOST:-}"
export APP_FULCRUM_PORT="${APP_FULCRUM_PORT:-50001}"
