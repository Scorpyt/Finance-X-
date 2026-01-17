# Environment Variables Setup Guide for Jarvis

## Overview

The Jarvis application requires environment variables for:
- **Email authentication** (Gmail SMTP)
- **Server configuration** (port settings)
- **API endpoints** (frontend-backend communication)

---

## Local Development Setup

### 1. Create `.env` File

Copy the `.env.example` file to `.env` in the `jarvis` directory:

```bash
cd jarvis
copy .env.example .env
```

### 2. Configure Environment Variables

Edit the `.env` file with your actual values:

```env
# Email Service Configuration (Gmail SMTP)
EMAIL_USER=your-actual-email@gmail.com
EMAIL_PASS=your-16-character-app-password

# Auth Server Port
AUTH_PORT=3001
```

### 3. Get Gmail App Password

**Important:** You need a Gmail App Password, not your regular password.

1. **Enable 2-Step Verification:**
   - Go to [Google Account Security](https://myaccount.google.com/security)
   - Enable "2-Step Verification"

2. **Create App Password:**
   - Go to [App Passwords](https://myaccount.google.com/apppasswords)
   - Select "Mail" as the app
   - Select "Other" as the device and name it "Jarvis"
   - Click "Generate"
   - Copy the 16-character password (format: `xxxx xxxx xxxx xxxx`)

3. **Add to `.env`:**
   ```env
   EMAIL_USER=youremail@gmail.com
   EMAIL_PASS=abcdabcdabcdabcd
   ```

### 4. Load Environment Variables in Node.js

The auth server already reads environment variables using `process.env`:

```javascript
const transporter = nodemailer.createTransport({
    service: 'gmail',
    auth: {
        user: process.env.EMAIL_USER || 'your-email@gmail.com',
        pass: process.env.EMAIL_PASS || 'your-app-password'
    }
});
```

For better environment variable management, you can install `dotenv`:

```bash
npm install dotenv
```

Then add to the top of `auth-server.cjs`:

```javascript
require('dotenv').config();
```

---

## Render Deployment Setup

### Environment Variables for Backend (`jarvis-auth-server`)

In the Render dashboard for your auth server:

1. Go to **Environment** tab
2. Add these variables:

| Key | Value | Description |
|-----|-------|-------------|
| `EMAIL_USER` | `your-email@gmail.com` | Gmail address for sending codes |
| `EMAIL_PASS` | `abcdabcdabcdabcd` | 16-char Gmail App Password |
| `AUTH_PORT` | `10000` | Port (Render uses 10000) |
| `NODE_ENV` | `production` | Environment mode |

**Note:** `AUTH_PORT` and `NODE_ENV` are already set in `render.yaml`, but you can override them if needed.

### Environment Variables for Frontend (`jarvis-frontend`)

The frontend needs to know the backend API URL:

| Key | Value | Description |
|-----|-------|-------------|
| `VITE_AUTH_API_URL` | Auto-set from backend | API endpoint URL |

**Note:** This is automatically set via the `render.yaml` configuration:

```yaml
envVars:
  - key: VITE_AUTH_API_URL
    fromService:
      type: web
      name: jarvis-auth-server
      envVarKey: RENDER_EXTERNAL_URL
```

---

## Using Environment Variables in Code

### Backend (Node.js)

```javascript
// Reading environment variables
const emailUser = process.env.EMAIL_USER;
const emailPass = process.env.EMAIL_PASS;
const port = process.env.AUTH_PORT || 3001;
const nodeEnv = process.env.NODE_ENV || 'development';

// Example usage
const transporter = nodemailer.createTransport({
    service: 'gmail',
    auth: {
        user: emailUser,
        pass: emailPass
    }
});

app.listen(port, () => {
    console.log(`Server running on port ${port}`);
});
```

### Frontend (Vite/React)

Vite exposes environment variables prefixed with `VITE_`:

```javascript
// In your React components or API calls
const API_URL = import.meta.env.VITE_AUTH_API_URL || 'http://localhost:3001';

// Example API call
fetch(`${API_URL}/api/auth/check-email`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email })
});
```

**Important:** 
- Vite only exposes variables prefixed with `VITE_`
- Environment variables are embedded at build time
- Don't store secrets in frontend environment variables (they're visible in the browser)

---

## Security Best Practices

### ✅ DO:
- Use `.env` files for local development
- Add `.env` to `.gitignore` (already done)
- Use Render's environment variable dashboard for production
- Use Gmail App Passwords, never your actual password
- Rotate App Passwords periodically

### ❌ DON'T:
- Commit `.env` files to Git
- Share your `.env` file or App Password
- Use your regular Gmail password
- Store secrets in frontend environment variables
- Hardcode sensitive values in your code

---

## Troubleshooting

### Email Not Sending

**Problem:** Auth server can't send emails

**Solutions:**
1. Verify `EMAIL_USER` is correct
2. Verify `EMAIL_PASS` is a 16-character App Password (not regular password)
3. Ensure 2FA is enabled on your Google Account
4. Check that Gmail SMTP is not blocked by your network
5. Check Render logs for specific error messages

### Frontend Can't Connect to Backend

**Problem:** Frontend shows connection errors

**Solutions:**
1. Verify `VITE_AUTH_API_URL` is set correctly
2. Check that the backend service is running (check Render dashboard)
3. Verify CORS is enabled in the backend (already configured)
4. Check browser console for specific error messages

### Port Conflicts

**Problem:** Port already in use locally

**Solutions:**
1. Change `AUTH_PORT` in `.env` to a different port (e.g., 3002)
2. Kill the process using the port
3. Use a different port for development

---

## Environment Variable Reference

### Backend Variables

```env
# Required
EMAIL_USER=your-email@gmail.com          # Gmail address
EMAIL_PASS=abcdabcdabcdabcd              # Gmail App Password

# Optional (with defaults)
AUTH_PORT=3001                            # Server port (default: 3001, Render: 10000)
NODE_ENV=development                      # Environment mode (development/production)
```

### Frontend Variables

```env
# Set automatically on Render, or manually for local dev
VITE_AUTH_API_URL=http://localhost:3001  # Backend API URL
```

---

## Quick Start Commands

### Local Development

```bash
# 1. Navigate to jarvis directory
cd jarvis

# 2. Install dependencies
npm install

# 3. Create and configure .env file
copy .env.example .env
# Edit .env with your Gmail credentials

# 4. Start auth server
npm run auth

# 5. In another terminal, start frontend
npm run dev
```

### Render Deployment

1. Push code to GitHub (already done ✅)
2. Create services in Render using Blueprint
3. Set environment variables in Render dashboard
4. Services will automatically deploy

---

## Additional Resources

- [Gmail App Passwords Guide](https://support.google.com/accounts/answer/185833)
- [Render Environment Variables Docs](https://docs.render.com/environment-variables)
- [Vite Environment Variables Docs](https://vitejs.dev/guide/env-and-mode.html)
- [Node.js process.env Documentation](https://nodejs.org/api/process.html#processenv)
