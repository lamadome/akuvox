# Akuvox Integration Fixes

This update includes several important fixes to address router crashes and connection issues with the Akuvox integration.

## Changes Made

### 1. Router Crash Prevention
- **Reduced Polling Frequency**: Changed from polling every 2 seconds to every 5 minutes (300 seconds), reducing network traffic by 150x
- **Improved Connection Management**: Added proper connection cleanup with "Connection: close" headers
- **Session Management**: Using proper session management to prevent connection leaks

### 2. Error Handling
- **Host Validation**: Added checks to prevent connections to invalid hosts (like 'none')
- **Fixed Date Format Issues**: Now supports multiple date formats for temporary key timestamps
- **Better Exception Handling**: Added comprehensive error handling throughout the codebase

### 3. Network Resilience
- **Increased Timeouts**: Extended request timeouts to handle slower connections
- **Proper Session Cleanup**: Ensured all sessions are properly closed after use

## If You Still Experience Issues

If you still have router crashes or connection problems:

1. **Check your logs** for specific error messages
2. **Further increase polling interval**:
   - Edit `custom_components/akuvox/door_poll.py` 
   - Change the interval value (default is now 300 seconds)
   - Restart Home Assistant
3. **Verify your network setup**:
   - Make sure your Akuvox device has stable connectivity
   - Check if your router has connection tracking limits that could be increased

## Technical Details

The main cause of router crashes was the excessive number of connections being created by the polling mechanism. This update maintains the functionality while making it much less aggressive on your network infrastructure.

Door events will still be detected, but with a delay of up to 5 minutes compared to real-time. This compromise allows the integration to function without overloading consumer-grade routers. 