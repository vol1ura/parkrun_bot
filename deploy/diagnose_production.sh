#!/bin/bash
# Production Environment Diagnostic Script
# This script checks common issues with production deployment

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "========================================="
echo "Parkrun Bot Production Diagnostic"
echo "========================================="
echo ""

# Function to check status
check_status() {
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓${NC} $1"
    else
        echo -e "${RED}✗${NC} $1"
    fi
}

# 1. Check .env file exists
echo "1. Checking .env file..."
if [ -f ".env" ]; then
    check_status ".env file exists"
else
    echo -e "${RED}✗ .env file NOT found${NC}"
    echo "  Please create .env file from deploy/env.production.example"
    exit 1
fi

# 2. Check PRODUCTION variable
echo ""
echo "2. Checking PRODUCTION variable..."
if grep -q "^PRODUCTION=" .env 2>/dev/null; then
    PROD_VALUE=$(grep "^PRODUCTION=" .env | cut -d'=' -f2)
    if [[ "$PROD_VALUE" =~ ^(true|1|yes)$ ]]; then
        check_status "PRODUCTION is enabled: $PROD_VALUE"
    else
        echo -e "${YELLOW}⚠${NC} PRODUCTION is set but not enabled: $PROD_VALUE"
        echo "  Set PRODUCTION=true (or 1, or yes) in .env"
    fi
else
    echo -e "${RED}✗ PRODUCTION variable is NOT set or commented out${NC}"
    echo "  Uncomment and set PRODUCTION=true in .env"
    exit 1
fi

# 3. Check HOST variable
echo ""
echo "3. Checking HOST variable..."
if grep -q "^HOST=" .env 2>/dev/null; then
    HOST_VALUE=$(grep "^HOST=" .env | cut -d'=' -f2)
    if [[ "$HOST_VALUE" =~ ^https?:// ]]; then
        check_status "HOST is set with protocol: $HOST_VALUE"
    else
        echo -e "${YELLOW}⚠${NC} HOST is set but missing protocol: $HOST_VALUE"
        echo "  HOST should be: https://$HOST_VALUE"
    fi
else
    echo -e "${RED}✗ HOST variable is NOT set${NC}"
    echo "  Set HOST=https://yourdomain.com in .env"
    exit 1
fi

# 4. Check BOT TOKEN
echo ""
echo "4. Checking BOT TOKEN..."
if grep -q "^API_BOT_TOKEN=" .env 2>/dev/null; then
    check_status "API_BOT_TOKEN is set"
else
    echo -e "${RED}✗ API_BOT_TOKEN is NOT set${NC}"
    exit 1
fi

# 5. Check WEBHOOK path
echo ""
echo "5. Checking WEBHOOK path..."
if grep -q "^WEBHOOK=" .env 2>/dev/null; then
    WEBHOOK_VALUE=$(grep "^WEBHOOK=" .env | cut -d'=' -f2)
    check_status "WEBHOOK path is set: /bot/$WEBHOOK_VALUE"
else
    echo -e "${RED}✗ WEBHOOK variable is NOT set${NC}"
    exit 1
fi

# 6. Check DATABASE_URL
echo ""
echo "6. Checking DATABASE_URL..."
if grep -q "^DATABASE_URL=" .env 2>/dev/null; then
    check_status "DATABASE_URL is set"
else
    echo -e "${RED}✗ DATABASE_URL is NOT set${NC}"
    exit 1
fi

# 7. Check PORT
echo ""
echo "7. Checking PORT..."
if grep -q "^PORT=" .env 2>/dev/null; then
    PORT_VALUE=$(grep "^PORT=" .env | cut -d'=' -f2)
    check_status "PORT is set: $PORT_VALUE"
else
    echo -e "${YELLOW}⚠${NC} PORT not set, will use default: 5000"
fi

# 8. Check if port is listening
echo ""
echo "8. Checking if application is running on port ${PORT_VALUE:-5000}..."
if command -v lsof &> /dev/null; then
    if lsof -i :${PORT_VALUE:-5000} &> /dev/null; then
        check_status "Port ${PORT_VALUE:-5000} is listening"
    else
        echo -e "${YELLOW}⚠${NC} Port ${PORT_VALUE:-5000} is NOT listening"
        echo "  Bot may not be running"
    fi
else
    echo -e "${YELLOW}⚠${NC} lsof not available, skipping port check"
fi

# 9. Check Python dependencies
echo ""
echo "9. Checking Python dependencies..."
if [ -f "requirements.txt" ]; then
    if command -v python3 &> /dev/null; then
        if python3 -c "import aiogram" 2>/dev/null; then
            check_status "Python dependencies installed (aiogram found)"
        else
            echo -e "${RED}✗ Python dependencies NOT installed${NC}"
            echo "  Run: pip install -r requirements.txt"
        fi
    else
        echo -e "${RED}✗ Python3 not found${NC}"
    fi
else
    echo -e "${YELLOW}⚠${NC} requirements.txt not found"
fi

# 10. Test webhook URL
echo ""
echo "10. Testing webhook URL accessibility..."
if command -v curl &> /dev/null; then
    if grep -q "^API_BOT_TOKEN=" .env && grep -q "^HOST=" .env; then
        BOT_TOKEN=$(grep "^API_BOT_TOKEN=" .env | cut -d'=' -f2)
        if curl -s "https://api.telegram.org/bot$BOT_TOKEN/getWebhookInfo" > /tmp/webhook_info.json; then
            WEBHOOK_URL=$(python3 -c "import json; print(json.load(open('/tmp/webhook_info.json'))['result'].get('url', 'NOT SET'))" 2>/dev/null || echo "ERROR")
            if [ "$WEBHOOK_URL" != "NOT SET" ] && [ "$WEBHOOK_URL" != "ERROR" ]; then
                check_status "Webhook is set in Telegram: $WEBHOOK_URL"

                # Check if webhook URL matches .env
                EXPECTED_HOST=$(grep "^HOST=" .env | cut -d'=' -f2)
                EXPECTED_WEBHOOK=$(grep "^WEBHOOK=" .env | cut -d'=' -f2)
                if [[ "$WEBHOOK_URL" == *"$EXPECTED_WEBHOOK"* ]]; then
                    check_status "Webhook URL matches configuration"
                else
                    echo -e "${YELLOW}⚠${NC} Webhook URL doesn't match configuration"
                    echo "  Expected: $EXPECTED_HOST/bot/$EXPECTED_WEBHOOK"
                    echo "  Got: $WEBHOOK_URL"
                fi
            else
                echo -e "${YELLOW}⚠${NC} Webhook is NOT set in Telegram"
                echo "  Run the bot to set webhook automatically"
            fi
            rm -f /tmp/webhook_info.json
        else
            echo -e "${RED}✗ Failed to get webhook info from Telegram${NC}"
        fi
    fi
else
    echo -e "${YELLOW}⚠${NC} curl not available, skipping webhook test"
fi

echo ""
echo "========================================="
echo "Diagnostic Complete"
echo "========================================="
echo ""
echo "Summary of required .env variables:"
echo "  PRODUCTION=true"
echo "  HOST=https://yourdomain.com"
echo "  API_BOT_TOKEN=your_token"
echo "  WEBHOOK=your_secret_path"
echo "  DATABASE_URL=postgresql://..."
echo "  PORT=5000"
echo ""
echo "Nginx upstream configuration required:"
echo "  upstream parkrun_bot {"
echo "      server 127.0.0.1:5000 fail_timeout=0;"
echo "  }"
echo ""
