# 🚀 Deploying Jarvis to Render

This guide walks you through deploying the Jarvis Architecture Visualizer to Render.

## Prerequisites

- GitHub account with the FinanceX repository
- Render account (free tier works)
- Gmail account with App Password for email authentication

## Step 1: Push to GitHub

Ensure the `jarvis` folder is committed and pushed to your GitHub repository:

```bash
cd c:\Users\yessm\Desktop\FinanceX
git add jarvis/
git commit -m "Add Jarvis application with Render deployment config"
git push origin main
```

## Step 2: Create Render Account

1. Go to [render.com](https://render.com)
2. Sign up or log in
3. Connect your GitHub account

## Step 3: Deploy Using Blueprint

1. In Render dashboard, click **"New"** → **"Blueprint"**
2. Connect your GitHub repository: `Scorpyt/Finance-X-`
3. Render will detect the `render.yaml` file in the `jarvis` folder
4. Click **"Apply"** to create both services

## Step 4: Configure Environment Variables

### For `jarvis-auth-server`:

1. Go to the auth server service in Render dashboard
2. Navigate to **Environment** tab
3. Add these variables:
   - `EMAIL_USER`: Your Gmail address (e.g., `youremail@gmail.com`)
   - `EMAIL_PASS`: Your Gmail App Password (16 characters)
   - `AUTH_PORT`: `10000` (already set in render.yaml)
   - `NODE_ENV`: `production` (already set in render.yaml)

**Getting Gmail App Password:**
1. Enable 2-Step Verification on your Google Account
2. Go to: Google Account → Security → 2-Step Verification → App passwords
3. Generate a new app password for "Mail"
4. Copy the 16-character password

### For `jarvis-frontend`:

The `VITE_AUTH_API_URL` is automatically set from the auth server's URL via the blueprint configuration.

## Step 5: Verify Deployment

1. **Check Build Logs**: Ensure both services build successfully
2. **Auth Server**: Visit `https://jarvis-auth-server.onrender.com/api/auth/status` to verify it's running
3. **Frontend**: Visit your frontend URL (e.g., `https://jarvis-frontend.onrender.com`)
4. **Test Authentication**: 
   - Enter one of the authorized emails
   - Check your email for the security code
   - Enter the code to access the application

## Troubleshooting

### Email Not Sending
- Verify `EMAIL_USER` and `EMAIL_PASS` are correct
- Ensure 2FA is enabled on Gmail
- Check that you're using an App Password, not your regular password

### Frontend Can't Connect to Backend
- Check that `VITE_AUTH_API_URL` is set correctly
- Verify the auth server is running and healthy

### Build Failures
- Check the build logs in Render dashboard
- Ensure all dependencies are in `package.json`

## URLs

After deployment, you'll have:
- **Frontend**: `https://jarvis-frontend.onrender.com`
- **Auth Server**: `https://jarvis-auth-server.onrender.com`

## Notes

- Free tier services may spin down after inactivity (takes ~30 seconds to wake up)
- Security codes rotate every hour automatically
- Only the 3 authorized emails can access the system
