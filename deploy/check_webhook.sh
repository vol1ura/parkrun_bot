#!/bin/bash

# Script to check Telegram Bot webhook status
# Usage: ./check_webhook.sh [bot_token]

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Get bot token
if [ -z "$1" ]; then
    # Try to read from .env file
    if [ -f "../.env" ]; then
        BOT_TOKEN=$(grep "^API_BOT_TOKEN=" ../.env | cut -d '=' -f2)
    elif [ -f ".env" ]; then
        BOT_TOKEN=$(grep "^API_BOT_TOKEN=" .env | cut -d '=' -f2)
    fi

    if [ -z "$BOT_TOKEN" ]; then
        echo -e "${RED}Error: Bot token not found${NC}"
        echo "Usage: $0 [bot_token]"
        echo "Or place .env file in project root with API_BOT_TOKEN"
        exit 1
    fi
else
    BOT_TOKEN=$1
fi

echo -e "${YELLOW}Checking webhook status...${NC}\n"

# Get webhook info
RESPONSE=$(curl -s "https://api.telegram.org/bot${BOT_TOKEN}/getWebhookInfo")

# Check if request was successful
if [ $? -ne 0 ]; then
    echo -e "${RED}Error: Failed to connect to Telegram API${NC}"
    exit 1
fi

# Pretty print JSON response
echo "$RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$RESPONSE"

echo -e "\n${YELLOW}Analysis:${NC}"

# Parse response
IS_OK=$(echo "$RESPONSE" | grep -o '"ok":true')
WEBHOOK_URL=$(echo "$RESPONSE" | grep -o '"url":"[^"]*"' | cut -d'"' -f4)
PENDING_COUNT=$(echo "$RESPONSE" | grep -o '"pending_update_count":[0-9]*' | cut -d':' -f2)
LAST_ERROR=$(echo "$RESPONSE" | grep -o '"last_error_message":"[^"]*"' | cut -d'"' -f4)

if [ -z "$IS_OK" ]; then
    echo -e "${RED}✗ Request failed${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Connection successful${NC}"

if [ -z "$WEBHOOK_URL" ]; then
    echo -e "${RED}✗ Webhook not set (polling mode or not configured)${NC}"
    echo -e "${YELLOW}  To set webhook, ensure PRODUCTION=true in .env${NC}"
else
    echo -e "${GREEN}✓ Webhook is set${NC}"
    echo -e "  URL: ${WEBHOOK_URL}"
fi

if [ -n "$PENDING_COUNT" ] && [ "$PENDING_COUNT" -gt 0 ]; then
    echo -e "${YELLOW}⚠ Pending updates: ${PENDING_COUNT}${NC}"
    echo -e "  This might indicate the webhook is not processing updates"
else
    echo -e "${GREEN}✓ No pending updates${NC}"
fi

if [ -n "$LAST_ERROR" ]; then
    echo -e "${RED}✗ Last error: ${LAST_ERROR}${NC}"
else
    echo -e "${GREEN}✓ No recent errors${NC}"
fi

# Additional checks
echo -e "\n${YELLOW}Additional checks:${NC}"

# Check if webhook URL is HTTPS
if [[ "$WEBHOOK_URL" == https://* ]]; then
    echo -e "${GREEN}✓ Webhook uses HTTPS${NC}"
elif [ -n "$WEBHOOK_URL" ]; then
    echo -e "${RED}✗ Webhook must use HTTPS${NC}"
fi

echo ""
