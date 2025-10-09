#!/bin/bash
# ============================================================================
# DAFU CLI - Test Script
# ============================================================================
# This script tests that the CLI tool is working correctly

set -e

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}"
echo "============================================================"
echo "  DAFU CLI Tool - Test Suite"
echo "============================================================"
echo -e "${NC}"

# Test 1: Check if CLI is installed
echo -e "${YELLOW}Test 1: Checking CLI installation...${NC}"
if command -v dafu &> /dev/null; then
    echo -e "${GREEN}✓ DAFU CLI is installed${NC}"
else
    echo -e "${RED}✗ DAFU CLI is not installed${NC}"
    echo "Install with: pip install -e ."
    exit 1
fi

# Test 2: Check CLI version
echo -e "\n${YELLOW}Test 2: Checking version...${NC}"
dafu --version
echo -e "${GREEN}✓ Version check passed${NC}"

# Test 3: Check help
echo -e "\n${YELLOW}Test 3: Checking help command...${NC}"
dafu --help > /dev/null
echo -e "${GREEN}✓ Help command works${NC}"

# Test 4: Check info command
echo -e "\n${YELLOW}Test 4: Checking info command...${NC}"
dafu info
echo -e "${GREEN}✓ Info command works${NC}"

# Test 5: Check models command
echo -e "\n${YELLOW}Test 5: Checking models command...${NC}"
dafu models
echo -e "${GREEN}✓ Models command works${NC}"

# Test 6: Docker tests (if Docker is running)
echo -e "\n${YELLOW}Test 6: Docker integration tests...${NC}"
if docker ps &> /dev/null; then
    echo -e "${BLUE}Building Docker image...${NC}"
    docker-compose build dafu-cli > /dev/null 2>&1 || true
    
    echo -e "${BLUE}Starting CLI container...${NC}"
    docker-compose --profile cli up -d
    
    # Wait for container to be ready
    sleep 5
    
    echo -e "${BLUE}Testing CLI in container...${NC}"
    docker exec dafu-cli dafu --version
    docker exec dafu-cli dafu info
    docker exec dafu-cli dafu models
    
    echo -e "${GREEN}✓ Docker integration tests passed${NC}"
    
    echo -e "\n${YELLOW}Cleaning up...${NC}"
    docker-compose down
else
    echo -e "${YELLOW}⚠️  Docker not running, skipping Docker tests${NC}"
fi

# Summary
echo -e "\n${GREEN}"
echo "============================================================"
echo "  All Tests Passed! ✓"
echo "============================================================"
echo -e "${NC}"

echo -e "\n${BLUE}Quick Start:${NC}"
echo "  make start-cli          # Start CLI in Docker"
echo "  make shell-cli          # Run fraud detection"
echo "  dafu fraud-detection    # Run locally"
echo ""

