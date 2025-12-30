# API Setup Guide

This guide walks you through setting up all the required APIs for Nekira Agent.

## Overview

Nekira Agent requires the following APIs:

| API | Purpose | Required? |
|-----|---------|-----------|
| Google Cloud / Vertex AI | LLM inference (Gemini) | ✅ Yes |
| Replicate | AI image generation | ✅ Yes |
| Twitter API v2 | Posting tweets | ✅ Yes |
| Twitter Data API | Fetching tweet data | ✅ Yes |

---

## Google Cloud / Vertex AI

The agent uses Google's Gemini models via Vertex AI for LLM inference.

### Step 1: Create a Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Note your **Project ID**

### Step 2: Enable Vertex AI API

1. Go to **APIs & Services** → **Library**
2. Search for "Vertex AI API"
3. Click **Enable**

### Step 3: Create Service Account

1. Go to **IAM & Admin** → **Service Accounts**
2. Click **Create Service Account**
3. Name: `nekira-agent`
4. Grant role: **Vertex AI User**
5. Click **Create Key** → **JSON**
6. Download the JSON key file

### Step 4: Configure Environment

```env
GOOGLE_CLOUD_PROJECT_ID=your-project-id
GOOGLE_APPLICATION_CREDENTIALS=/path/to/your-service-account.json
VERTEX_AI_LOCATION=us-central1
VERTEX_AI_MODEL_ID=gemini-2.0-flash
```

### Supported Locations
- `us-central1` (recommended)
- `europe-west4`
- `asia-northeast1`

---

## Replicate

Used for AI image generation with Flux models.

### Step 1: Create Account

1. Go to [Replicate](https://replicate.com/)
2. Sign up with GitHub or email

### Step 2: Get API Token

1. Go to [Account Settings](https://replicate.com/account/api-tokens)
2. Click **Create token**
3. Copy the token (starts with `r8_`)

### Step 3: Configure Environment

```env
REPLICATE_API_TOKEN=r8_your_token_here
```

### Pricing
- Pay-per-use model
- Flux 1.1 Pro Ultra: ~$0.06 per image
- Check current pricing at [replicate.com/pricing](https://replicate.com/pricing)

---

## Twitter API

Required for posting tweets and uploading media.

### Step 1: Apply for Developer Access

1. Go to [Twitter Developer Portal](https://developer.twitter.com/)
2. Sign up for a developer account
3. Choose **Free** or **Basic** tier

### Step 2: Create an App

1. Go to **Projects & Apps** → **Create App**
2. Name your app (e.g., "Nekira Agent")
3. Note your **API Key** and **API Secret**

### Step 3: Generate Access Tokens

1. Go to your app's **Keys and Tokens** tab
2. Under **Access Token and Secret**, click **Generate**
3. Save both values (you won't see them again!)

### Step 4: Set Permissions

1. Go to **Settings** tab
2. Under **App permissions**, select **Read and Write**
3. Save changes

### Step 5: Configure Environment

```env
TWITTER_CONSUMER_KEY=your_api_key
TWITTER_CONSUMER_SECRET=your_api_secret
TWITTER_ACCESS_TOKEN=your_access_token
TWITTER_ACCESS_TOKEN_SECRET=your_access_token_secret
```

### Rate Limits

| Tier | Monthly Tweet Limit |
|------|---------------------|
| Free | 1,500 tweets |
| Basic ($100/mo) | 3,000 tweets |
| Pro ($5,000/mo) | 300,000 tweets |

---

## Twitter Data API (twitterapi.io)

Used for fetching tweet data including media and thread context.

### Step 1: Get API Key

1. Go to [twitterapi.io](https://twitterapi.io/)
2. Sign up for an account
3. Get your API key from the dashboard

### Step 2: Configure Environment

```env
TWITTERAPI_KEY=your_twitterapi_key
```

### Alternative: Twitter API v2

If you prefer to use the official Twitter API for data fetching, you can modify `processing_pipeline/data_extractor.py` to use the Twitter API v2 endpoints directly.

---

## Complete .env Example

```env
# ============================================
# Nekira Agent - Full Configuration
# ============================================

# --- Google Cloud / Vertex AI ---
GOOGLE_CLOUD_PROJECT_ID=my-project-123456
GOOGLE_APPLICATION_CREDENTIALS=/home/user/keys/gcp-key.json
VERTEX_AI_LOCATION=us-central1
VERTEX_AI_MODEL_ID=gemini-2.0-flash

# --- Replicate ---
REPLICATE_API_TOKEN=r8_abc123def456...

# --- Twitter API (OAuth 1.0a) ---
TWITTER_CONSUMER_KEY=abc123...
TWITTER_CONSUMER_SECRET=xyz789...
TWITTER_ACCESS_TOKEN=12345-abcdef...
TWITTER_ACCESS_TOKEN_SECRET=ghijkl...

# --- Twitter Data API ---
TWITTERAPI_KEY=your_key_here

# --- Agent Configuration ---
ACTIVE_CHARACTER=nekira
```

---

## Verification

After setting up all APIs, verify your configuration:

```bash
# Check if environment is loaded correctly
python -c "from twitter_post_analyzer.constants import *; print('Config OK')"

# List available characters
python main.py --list-characters

# Dry run test
python main.py https://x.com/elonmusk/status/1234567890 --dry-run
```

---

## Troubleshooting

### Google Cloud Issues

**Error:** `Could not automatically determine credentials`
- Ensure `GOOGLE_APPLICATION_CREDENTIALS` points to valid JSON file
- Check file permissions

**Error:** `Vertex AI API has not been enabled`
- Enable API in Google Cloud Console

### Replicate Issues

**Error:** `401 Unauthorized`
- Check if token is correct
- Ensure token hasn't expired

### Twitter Issues

**Error:** `403 Forbidden`
- Check app permissions (needs Read and Write)
- Regenerate access tokens after changing permissions

**Error:** `429 Too Many Requests`
- Rate limit exceeded
- Wait and retry, or upgrade tier

---

## Security Notes

⚠️ **Never commit your `.env` file to git!**

- The `.gitignore` already excludes `.env`
- Use `.env.example` as a template
- For production, use proper secret management
