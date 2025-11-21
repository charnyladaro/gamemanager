#!/bin/bash

# ============================================
# GameManager Build Script (Bash)
# Builds both GameManager.exe and GameManagerAdmin.exe
# ============================================

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Store the root directory
ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"

echo ""
echo "============================================"
echo "   GameManager Build Script"
echo "============================================"
echo ""

# ============================================
# Build Frontend (GameManager.exe)
# ============================================

echo -e "${BLUE}[1/2] Building GameManager (Frontend)...${NC}"
echo ""

cd "$ROOT_DIR/frontend" || exit 1

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo -e "${YELLOW}Installing frontend dependencies...${NC}"
    npm install
    if [ $? -ne 0 ]; then
        echo -e "${RED}ERROR: Failed to install frontend dependencies${NC}"
        exit 1
    fi
fi

echo "Building GameManager.exe..."
npm run build:win
if [ $? -ne 0 ]; then
    echo -e "${RED}ERROR: Failed to build GameManager${NC}"
    cd "$ROOT_DIR"
    exit 1
fi

echo ""
echo -e "${GREEN}[SUCCESS] GameManager built successfully!${NC}"
echo "Location: $ROOT_DIR/frontend/dist/"
echo ""

# ============================================
# Build Admin Dashboard (GameManagerAdmin.exe)
# ============================================

echo -e "${BLUE}[2/2] Building GameManagerAdmin (Admin Dashboard)...${NC}"
echo ""

cd "$ROOT_DIR/admin-dashboard" || exit 1

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo -e "${YELLOW}Installing admin dashboard dependencies...${NC}"
    npm install
    if [ $? -ne 0 ]; then
        echo -e "${RED}ERROR: Failed to install admin dashboard dependencies${NC}"
        cd "$ROOT_DIR"
        exit 1
    fi
fi

echo "Building GameManagerAdmin.exe..."
npm run build
if [ $? -ne 0 ]; then
    echo -e "${RED}ERROR: Failed to build GameManagerAdmin${NC}"
    cd "$ROOT_DIR"
    exit 1
fi

echo ""
echo -e "${GREEN}[SUCCESS] GameManagerAdmin built successfully!${NC}"
echo "Location: $ROOT_DIR/admin-dashboard/dist/"
echo ""

# ============================================
# Build Complete
# ============================================

cd "$ROOT_DIR"

echo "============================================"
echo "   BUILD COMPLETE!"
echo "============================================"
echo ""
echo "Built Applications:"
echo "  1. GameManager.exe"
echo "     Location: $ROOT_DIR/frontend/dist/win-unpacked/GameManager.exe"
echo ""
echo "  2. GameManagerAdmin.exe"
echo "     Location: $ROOT_DIR/admin-dashboard/dist/win-unpacked/GameManagerAdmin.exe"
echo ""
echo "============================================"
echo ""
