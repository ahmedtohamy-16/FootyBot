# 🚀 FootyBot Deployment Guide - Phase 6

## Overview
This guide covers deploying FootyBot with the advanced points system and Telegram bot integration.

## Prerequisites

1. **Python 3.10+** installed
2. **Supabase Account** with database setup
3. **Telegram Bot Token** from [@BotFather](https://t.me/BotFather)
4. **API-Football Key** from [API-Sports](https://www.api-football.com/)

## Installation Steps

### 1. Clone Repository
```bash
git clone https://github.com/ahmedtohamy-16/FootyBot.git
cd FootyBot
```

### 2. Create Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Copy the example environment file:
```bash
cp .env.example .env
```

Edit `.env` and add your credentials:
```env
# Supabase Configuration
SUPABASE_URL=your_supabase_project_url
SUPABASE_KEY=your_supabase_anon_key
SUPABASE_SERVICE_KEY=your_supabase_service_role_key

# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
TELEGRAM_WEBHOOK_URL=https://your-domain.com/webhook  # Optional for webhooks
TELEGRAM_WEBHOOK_SECRET=your_webhook_secret  # Optional

# API-Football Configuration
API_FOOTBALL_KEY=your_api_football_key
API_FOOTBALL_HOST=v3.football.api-sports.io

# Environment
ENVIRONMENT=production
DEBUG=False
LOG_LEVEL=INFO
```

### 5. Setup Database

Run the migration scripts in your Supabase SQL Editor in this order:

1. **Base Schema** (if not already done):
   ```bash
   database/schema.sql
   ```

2. **Indexes** (if not already done):
   ```bash
   database/indexes.sql
   ```

3. **New Migration** (Phase 6 - Advanced Points):
   ```bash
   database/migrations/001_update_users_points.sql
   ```

This migration adds:
- `free_requests` column (3 daily free API requests)
- `premium_points` column (earned via referrals)
- `last_free_reset` column (tracks daily reset)
- `first_premium_warning_shown` column (UX feature)
- `referral_count` column
- Database functions: `reset_daily_free_requests()`, `deduct_point()`, `process_referral()`

### 6. Verify Installation

Test Python imports:
```bash
python -c "import telebot; print('pyTelegramBotAPI:', telebot.__version__)"
python -c "import supabase; print('Supabase: OK')"
python -c "from src.bot.main import bot; print('Bot initialized')"
```

### 7. Run the Bot

#### Development Mode:
```bash
python src/bot/main.py
```

#### Production Mode (with process manager):
```bash
# Using systemd
sudo cp deployment/footybot.service /etc/systemd/system/
sudo systemctl start footybot
sudo systemctl enable footybot

# Using PM2
pm2 start src/bot/main.py --name footybot --interpreter python3
pm2 save
```

## Bot Features

### Free Features (No Points Required)
- ℹ️ Bot info and user statistics
- 💰 Points balance
- 🎁 Referral system
- ⚙️ Settings
- 👕 Teams list (static data)
- 🏆 Leagues list (static data)
- 📊 Team info (static data)

### Features Requiring Points
Each costs 1 point (free or premium):
- ⚽ Live matches
- 📅 Today's matches
- 📆 Tomorrow's matches
- 📊 League standings
- 📊 Team statistics (API)

### Points System
- **Free Requests**: 3 per day (reset at midnight)
- **Premium Points**: Earned via referrals
  - Referrer gets: **+3 points**
  - New user gets: **+1 point**

### Commands
- `/start [referral_code]` - Start bot (optional referral code)
- `/info` - Show bot info and statistics
- `/help` - Show available commands

## Monitoring

### View Logs
```bash
# Live logs
tail -f logs/footybot_$(date +%Y-%m-%d).log

# Error logs
tail -f logs/errors_$(date +%Y-%m-%d).log

# API request logs
tail -f logs/api_requests_$(date +%Y-%m-%d).log
```

### Check Bot Status
```bash
# Using systemd
sudo systemctl status footybot

# Using PM2
pm2 status footybot
pm2 logs footybot
```

## Troubleshooting

### Bot Not Responding
1. Check bot token is correct
2. Verify network connectivity
3. Check logs for errors
4. Ensure all dependencies are installed

### Database Errors
1. Verify Supabase credentials
2. Check database migrations are applied
3. Review database logs in Supabase dashboard

### API Errors
1. Verify API-Football key is valid
2. Check API quota/limits
3. Review API request logs

## Scheduled Tasks

### Daily Free Requests Reset
Add a cron job or scheduled task to reset free requests daily:

```sql
-- Run this in Supabase via cron job or scheduler
SELECT reset_daily_free_requests();
```

Or use a cron job:
```bash
# Add to crontab (crontab -e)
0 0 * * * psql "$DATABASE_URL" -c "SELECT reset_daily_free_requests();"
```

## Security Considerations

1. **Never commit `.env` file** - Always use environment variables
2. **Secure Supabase keys** - Use service role key only on backend
3. **Rate limiting** - Already implemented in middleware
4. **Input validation** - Handled by bot framework
5. **SQL injection protection** - Using parameterized queries

## Performance Optimization

1. **Caching**:
   - Static data cached with 24-hour TTL
   - API responses cached per configuration
   
2. **Rate Limiting**:
   - User-level rate limiting via points system
   - API rate limiting to respect quotas

3. **Database Indexes**:
   - Applied via migration script
   - Optimized for common queries

## Backup & Recovery

### Database Backup
Supabase provides automatic backups. Additionally:
```bash
# Manual backup
pg_dump "$DATABASE_URL" > backup_$(date +%Y%m%d).sql
```

### Restore from Backup
```bash
psql "$DATABASE_URL" < backup_20250101.sql
```

## Scaling Considerations

1. **Horizontal Scaling**: Multiple bot instances with load balancer
2. **Database**: Supabase handles scaling automatically
3. **Redis**: Consider adding Redis for distributed caching
4. **Webhooks**: Use webhooks instead of polling for better performance

## Support

For issues or questions:
- GitHub Issues: https://github.com/ahmedtohamy-16/FootyBot/issues
- Documentation: Check README.md

---

**Built with ❤️ for football fans**
