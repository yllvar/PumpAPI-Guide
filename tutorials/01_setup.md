# Tutorial 01: Environment Setup

This guide walks you through setting up your development environment for pumpAPI.

## Prerequisites

- Python 3.10 or higher
- pip or uv package manager
- A code editor (VS Code recommended)
- Access to the pumpAPI API

## Step 1: Install Python

```bash
# macOS
brew install python@3.11

# Ubuntu/Debian
sudo apt-get update
sudo apt-get install python3.11

# Windows
# Download from python.org
```

Verify installation:

```bash
python --version
```

## Step 2: Clone the Repository

```bash
git clone https://github.com/yourusername/pumpAPI-guide.git
cd pumpAPI-guide
```

## Step 3: Create Virtual Environment

Using venv:

```bash
python -m venv venv
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows
```

Using uv (recommended):

```bash
uv venv
source .venv/bin/activate
```

## Step 4: Install Dependencies

```bash
pip install -e .
```

Or with uv:

```bash
uv pip install -e .
```

## Step 5: Configure Environment Variables

```bash
cp .env.example .env
```

Edit `.env` with your credentials:

```env
PUMPAPI_API_KEY=your_api_key_here
PUMPAPI_RPC_URL=https://api.mainnet-beta.solana.com
```

## Step 6: Verify Installation

```bash
python -c "from pumpapi import PumpApiClient; print('OK')"
```

## Step 7: Get an API Key

1. Visit pumpportal.fun
2. Sign up for an account
3. Generate an API key
4. Add it to your `.env` file

## Common Issues

### SSL Certificate Error

```bash
# macOS
/Applications/Python\ 3.11/Install\ Certificates.command
```

### Python Not Found

Make sure Python is in your PATH. On macOS:

```bash
export PATH="/usr/local/bin:$PATH"
```

### Permission Denied

Never run pip with sudo. Use virtual environments instead.

## Next Steps

Proceed to [Tutorial 02: First Trade](02_first_trade.md) to execute your first trade.
