# CP4I Chief Console - Monitoring Guide

Automated monitoring options for tracking CP4I installation and ongoing cluster health.

---

## Quick Start

**Watch CP4I Install (Recommended):**
```bash
# Run every 2 minutes with dashboard auto-open
python3 monitor.py --auto-open
```

**Press Ctrl+C to stop anytime**

---

## Monitoring Options

### Option 1: Python Monitor Script (Recommended)

**Basic Monitoring** - Every 2 minutes:
```bash
python3 monitor.py
```

**With Dashboard Auto-Open:**
```bash
python3 monitor.py --auto-open
```

**Custom Interval** - Every 5 minutes:
```bash
python3 monitor.py --interval 300
```

**Limited Runs** - Run 10 times then stop:
```bash
python3 monitor.py --max-runs 10
```

**Quick Testing** - Every 30 seconds, 20 times:
```bash
python3 monitor.py --interval 30 --max-runs 20 --auto-open
```

---

### Option 2: Unix `watch` Command

**Simple watch mode:**
```bash
watch -n 120 'python3 chief_console.py'
```

**With dashboard auto-open (macOS):**
```bash
watch -n 120 'python3 chief_console.py && open output/dashboard.html'
```

**With dashboard auto-open (Linux):**
```bash
watch -n 120 'python3 chief_console.py && xdg-open output/dashboard.html'
```

---

### Option 3: Background Cron Job

**Edit crontab:**
```bash
crontab -e
```

**Add entry to run every 5 minutes:**
```cron
*/5 * * * * cd /Users/jeffhans/Documents/ai_tools/chief-console && /usr/bin/python3 chief_console.py >> logs/monitor.log 2>&1
```

**Create logs directory first:**
```bash
mkdir -p logs
```

**View logs:**
```bash
tail -f logs/monitor.log
```

**Remove cron job:**
```bash
crontab -l  # List current jobs
crontab -r  # Remove all jobs
```

---

### Option 4: Background Process

**Run in background:**
```bash
nohup python3 monitor.py --interval 300 > logs/monitor.log 2>&1 &
```

**Check if running:**
```bash
ps aux | grep monitor.py
```

**Stop background process:**
```bash
# Find PID
ps aux | grep monitor.py

# Kill process
kill <PID>
```

---

## What You'll See

### Terminal Output

```
======================================================================
CP4I CHIEF CONSOLE - AUTOMATED MONITORING
======================================================================
Monitoring interval: 120 seconds (2 minutes)
Auto-open dashboard: Yes
Max runs: Unlimited

Press Ctrl+C to stop monitoring
======================================================================

======================================================================
RUN #1 - 2025-12-28 19:15:00
======================================================================

✅ No significant changes detected
   Collection complete!
   CP4I namespaces found: 2
   Total operators: 556
   CP4I operators: 1

✅ Collection #1 complete

⏳ Next run in 120 seconds...
   10s...
```

### When Changes Detected

```
======================================================================
RUN #5 - 2025-12-28 19:23:00
======================================================================

🟡 IMPORTANT: 3 change(s) detected
   📊 +3 new changes
   Collection complete!
   CP4I namespaces found: 3
   Total operators: 562
   CP4I operators: 2

✅ Collection #5 complete
📊 Dashboard opened: /Users/jeffhans/.../dashboard.html

⏳ Next run in 120 seconds...
```

### Critical Issues

```
======================================================================
RUN #8 - 2025-12-28 19:29:00
======================================================================

🔴 CRITICAL: 2 change(s) detected!
   ⚠️  +2 new critical issues!
   Collection complete!

✅ Collection #8 complete
```

---

## Recommended Settings

### During CP4I Installation

**Active monitoring** - Check frequently:
```bash
python3 monitor.py --interval 120 --auto-open
```
- Every 2 minutes
- Dashboard auto-opens to see changes
- Run until installation completes

### After Installation Complete

**Maintenance monitoring** - Less frequent:
```bash
python3 monitor.py --interval 600
```
- Every 10 minutes
- Just track health
- No auto-open needed

### Troubleshooting Issues

**Intensive monitoring** - Quick checks:
```bash
python3 monitor.py --interval 30 --max-runs 20 --auto-open
```
- Every 30 seconds
- 20 runs (10 minutes total)
- Auto-open to see changes immediately

---

## Stopping Monitoring

**Foreground Process:**
- Press `Ctrl+C`

**Background Process:**
```bash
# Find process
ps aux | grep monitor.py

# Kill it
kill <PID>

# Or kill all Python processes (careful!)
pkill -f monitor.py
```

**Cron Job:**
```bash
crontab -r
```

---

## Monitoring Output

### Dashboard Changes

The dashboard automatically shows "What Changed" in Wave 1 when differences are detected.

### Logs

**Create logs directory:**
```bash
mkdir -p logs
```

**Redirect output:**
```bash
python3 monitor.py --interval 300 > logs/monitor-$(date +%Y%m%d-%H%M%S).log 2>&1
```

**Tail logs in real-time:**
```bash
tail -f logs/monitor-*.log
```

---

## Tips

1. **Start with auto-open** during CP4I installation to see changes immediately
2. **Use shorter intervals** (60-120s) during active installation
3. **Use longer intervals** (300-600s) for ongoing monitoring
4. **Set max-runs** when testing to avoid forgetting to stop
5. **Run in background** for long-term monitoring
6. **Check logs** if running headless/remotely

---

## Troubleshooting

**Monitor not starting:**
- Check Python version: `python3 --version`
- Ensure chief_console.py works: `python3 chief_console.py`

**Dashboard not opening:**
- Check if file exists: `ls -la output/dashboard.html`
- Try opening manually: `open output/dashboard.html`

**High CPU usage:**
- Increase interval: `--interval 300` (5 minutes)
- Check cluster connection: `oc whoami`

**Process won't stop:**
- Use `kill -9 <PID>` for force kill
- Check for orphaned processes: `ps aux | grep python`

---

## Advanced Usage

### Email Alerts on Critical Changes

Create wrapper script:
```bash
#!/bin/bash
OUTPUT=$(python3 chief_console.py 2>&1)

if echo "$OUTPUT" | grep -q "🔴 CRITICAL"; then
    echo "$OUTPUT" | mail -s "CP4I Critical Alert" you@example.com
fi
```

### Slack Notifications

Use webhook in wrapper script:
```bash
#!/bin/bash
OUTPUT=$(python3 chief_console.py 2>&1)

if echo "$OUTPUT" | grep -q "🟡 IMPORTANT"; then
    curl -X POST -H 'Content-type: application/json' \
      --data '{"text":"CP4I changes detected!"}' \
      YOUR_SLACK_WEBHOOK_URL
fi
```

### Multiple Environments

```bash
# Monitor env 1
python3 env_manager.py activate env1
python3 monitor.py --interval 300 --max-runs 12 &

# Monitor env 2
python3 env_manager.py activate env2
python3 monitor.py --interval 300 --max-runs 12 &
```

---

## Examples

### Watch CP4I Installation

```bash
# Start monitoring
python3 monitor.py --interval 120 --auto-open

# You'll see:
# - Event Streams appearing
# - Kafka topics being created
# - Operators installing
# - Pods starting up

# Stop when done: Ctrl+C
```

### Daily Health Check

```bash
# Add to cron for daily 8am check
0 8 * * * cd /path/to/chief-console && python3 chief_console.py
```

### Continuous Background Monitoring

```bash
# Start background monitoring every 10 minutes
nohup python3 monitor.py --interval 600 > logs/monitor.log 2>&1 &

# Check status anytime
tail logs/monitor.log

# Or open dashboard manually
open output/dashboard.html
```

---

For more information, see main README.md
