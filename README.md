# PiePay Monitor (piepaymon)

A monitoring service for tracking and receiving notifications about interesting cashback offers from PiePay.

## Overview

PiePay Monitor automatically checks for available cashback deals that meet your criteria and notifies you when profitable opportunities arise. It runs as a background service and can send alerts via Telegram when new interesting offers are found.

## Features

- 🔍 Monitors PiePay for cashback deals meeting your criteria
- 💰 Configurable minimum cashback amount and payment ratio
- 🔔 Optional Telegram notifications

## Requirements

- Python 3.12 or higher
- PiePay account(s)
- Telegram bot (optional, for notifications)

## Installation

### Using Nix (recommended)

If you have Nix with flakes enabled:

```bash
# Clone the repository
git clone https://github.com/vipulog/piepaymon.git
cd piepaymon

# Enter development shell
nix develop

# Run directly
nix run
```

### Manual Installation

```bash
# Clone the repository
git clone https://github.com/vipulog/piepaymon.git
cd piepaymon

# Setup virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -e .
```

## Configuration

Copy the example environment file and adjust settings as needed:

```bash
cp .env-example .env
```

### Available Settings

| Setting | Description | Default |
|---------|-------------|---------|
| `MIN_CASHBACK` | Minimum cashback amount (₹) to consider an offer interesting | 100 |
| `MIN_DELAY` | Minimum delay between offer checks (seconds) | 1 |
| `MAX_DELAY` | Maximum delay between offer checks (seconds) | 5 |
| `MAX_PAYMENT` | Maximum payment amount (₹) to avoid large transactions | 100000 |
| `EARN_PAY_RATIO` | Acceptable ratio between cashback and payment | 0.03 |
| `MAX_ERRORS` | Maximum consecutive errors before exiting | 3 |
| `ERROR_DELAY_INCREMENT` | Additional delay after each error (seconds) | 1 |
| `NOTIF_ENABLE` | Whether to enable Telegram notifications | False |
| `NOTIF_BOT_TOKEN` | Telegram bot token for sending notifications | |
| `NOTIF_CHAT_ID` | Telegram chat ID where notifications will be sent | |

## Setting Up Telegram Notifications

1. **Create a Telegram Bot:**
   - Message [@BotFather](https://t.me/BotFather) on Telegram
   - Use the `/newbot` command and follow the instructions
   - Save the API token provided by BotFather

2. **Start a chat with your bot:**
   - Find your bot on Telegram and start a conversation
   - This is necessary for the bot to be able to send you messages

3. **Get your Chat ID:**
   - Message [@userinfobot](https://t.me/userinfobot) on Telegram
   - It will reply with your Chat ID

4. **Configure Notifications:**
   - Add these values to your `.env` file:
     ```
     NOTIF_ENABLE=True
     NOTIF_BOT_TOKEN=your_bot_token_here
     NOTIF_CHAT_ID=your_chat_id_here
     ```

## Usage

### Create a Session

Before running the monitor, you need to create a session:

```bash
piepaymon create-session
```

This will guide you through entering your phone number and OTP to create a session.

### Run the Monitor

Start the monitoring service:

```bash
piepaymon run
```

The service will continuously check for new offers matching your criteria and notify you when found.

### Exit the Monitor

Press `Ctrl+C` to gracefully stop the monitoring service.

## Important Note

**You need two PiePay accounts for this tool to be most effective:**
1. One account for monitoring deals
2. One account for actual transactions

You must maintain the same cards in both accounts for them to show identical deals. The monitoring account will detect profitable offers, and you can then use the transaction account to make the actual payments.

## Development

### Pre-commit Hooks

This project uses pre-commit hooks to ensure code quality:

```bash
pre-commit install
```

### Code Formatting

The project uses `treefmt` to handle code formatting:

```bash
treefmt
```

## License

[GLWT License](LICENSE)
