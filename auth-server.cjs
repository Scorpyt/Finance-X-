const express = require('express');
const nodemailer = require('nodemailer');
const cors = require('cors');
const crypto = require('crypto');

const app = express();
app.use(cors());
app.use(express.json());

// ==================== ENTERPRISE SECURITY CONFIG ====================

// AUTHORIZED USERS ONLY - No exceptions
const AUTHORIZED_EMAILS = [
    'yessmartypie880@gmail.com',
    'mohitk6469@gmail.com',
    'aryamannpareek@gmail.com'
];

// Current security code (rotates every hour)
let currentSecurityCode = '';
let codeGeneratedAt = 0;
const CODE_VALIDITY_MS = 60 * 60 * 1000; // 1 hour

// Access logs
const accessLogs = [];

// Email transporter (using Gmail SMTP)
// NOTE: You need to set up an App Password for Gmail
// Go to: Google Account > Security > 2-Step Verification > App passwords
const transporter = nodemailer.createTransport({
    service: 'gmail',
    auth: {
        user: process.env.EMAIL_USER || 'your-email@gmail.com',
        pass: process.env.EMAIL_PASS || 'your-app-password'
    }
});

// ==================== SECURITY CODE MANAGEMENT ====================

function generateSecurityCode() {
    // Generate cryptographically secure 6-digit code
    return crypto.randomInt(100000, 999999).toString();
}

function rotateSecurityCode() {
    currentSecurityCode = generateSecurityCode();
    codeGeneratedAt = Date.now();
    console.log(`\n🔐 [SECURITY] New code generated: ${currentSecurityCode}`);
    console.log(`   Valid until: ${new Date(codeGeneratedAt + CODE_VALIDITY_MS).toLocaleString()}\n`);

    // Send new code to all authorized users
    sendCodeToAllUsers();

    return currentSecurityCode;
}

function isCodeValid() {
    return Date.now() - codeGeneratedAt < CODE_VALIDITY_MS;
}

function getTimeUntilRotation() {
    const remaining = CODE_VALIDITY_MS - (Date.now() - codeGeneratedAt);
    const minutes = Math.floor(remaining / 60000);
    const seconds = Math.floor((remaining % 60000) / 1000);
    return { minutes, seconds, ms: remaining };
}

// ==================== EMAIL SERVICE ====================

async function sendSecurityCodeEmail(email) {
    const timeLeft = getTimeUntilRotation();

    const mailOptions = {
        from: `"JARVIS Security" <${process.env.EMAIL_USER || 'security@jarvis.local'}>`,
        to: email,
        subject: '🔐 JARVIS Access Code',
        html: `
      <!DOCTYPE html>
      <html>
      <head>
        <style>
          body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #0d1117; color: #c9d1d9; margin: 0; padding: 40px; }
          .container { max-width: 500px; margin: 0 auto; background: #161b22; border-radius: 16px; border: 1px solid #30363d; overflow: hidden; }
          .header { background: linear-gradient(135deg, #f6821f, #fbad41); padding: 30px; text-align: center; }
          .header h1 { color: white; margin: 0; font-size: 24px; }
          .content { padding: 30px; }
          .code-box { background: #0d1117; border: 2px solid #f6821f; border-radius: 12px; padding: 20px; text-align: center; margin: 20px 0; }
          .code { font-size: 36px; font-weight: 700; letter-spacing: 8px; color: #f6821f; font-family: monospace; }
          .timer { color: #8b949e; font-size: 14px; margin-top: 10px; }
          .warning { background: rgba(239, 68, 68, 0.1); border: 1px solid rgba(239, 68, 68, 0.3); border-radius: 8px; padding: 12px; margin-top: 20px; color: #ef4444; font-size: 13px; }
          .footer { padding: 20px 30px; border-top: 1px solid #30363d; color: #8b949e; font-size: 12px; text-align: center; }
        </style>
      </head>
      <body>
        <div class="container">
          <div class="header">
            <h1>🛡️ JARVIS Access</h1>
          </div>
          <div class="content">
            <p>Your enterprise security code for JARVIS Architecture Visualizer:</p>
            <div class="code-box">
              <div class="code">${currentSecurityCode}</div>
              <div class="timer">⏱️ Valid for ${timeLeft.minutes} minutes</div>
            </div>
            <p style="color: #8b949e; font-size: 14px;">
              This code will automatically rotate in ${timeLeft.minutes} minutes. 
              A new code will be sent to you when it expires.
            </p>
            <div class="warning">
              ⚠️ Do not share this code. This email was sent only to authorized personnel.
            </div>
          </div>
          <div class="footer">
            Secured by Cloudflare Zero Trust<br>
            JARVIS Enterprise Security System
          </div>
        </div>
      </body>
      </html>
    `
    };

    try {
        await transporter.sendMail(mailOptions);
        console.log(`✉️  Code sent to: ${email}`);
        return true;
    } catch (error) {
        console.error(`❌ Failed to send to ${email}:`, error.message);
        return false;
    }
}

async function sendCodeToAllUsers() {
    console.log('📧 Sending security codes to all authorized users...\n');
    for (const email of AUTHORIZED_EMAILS) {
        await sendSecurityCodeEmail(email);
    }
}

// ==================== API ENDPOINTS ====================

// Check if email is authorized
app.post('/api/auth/check-email', (req, res) => {
    const { email } = req.body;
    const normalizedEmail = email?.toLowerCase().trim();

    // Log access attempt
    accessLogs.push({
        timestamp: Date.now(),
        action: 'email_check',
        email: normalizedEmail,
        authorized: AUTHORIZED_EMAILS.includes(normalizedEmail),
        ip: req.ip
    });

    if (!AUTHORIZED_EMAILS.includes(normalizedEmail)) {
        console.log(`🚫 BLOCKED: Unauthorized email attempt: ${normalizedEmail}`);
        return res.status(403).json({
            success: false,
            error: 'ACCESS DENIED',
            message: 'This email is not authorized to access JARVIS. Only enterprise personnel with pre-approved access can use this system.'
        });
    }

    console.log(`✅ Authorized email: ${normalizedEmail}`);

    // Send the current code to this specific user
    sendSecurityCodeEmail(normalizedEmail);

    res.json({
        success: true,
        message: 'Security code sent to your email',
        expiresIn: getTimeUntilRotation()
    });
});

// Verify security code
app.post('/api/auth/verify', (req, res) => {
    const { email, code } = req.body;
    const normalizedEmail = email?.toLowerCase().trim();

    // Log verification attempt
    accessLogs.push({
        timestamp: Date.now(),
        action: 'code_verify',
        email: normalizedEmail,
        codeMatch: code === currentSecurityCode,
        ip: req.ip
    });

    // Double-check email authorization
    if (!AUTHORIZED_EMAILS.includes(normalizedEmail)) {
        console.log(`🚫 BLOCKED: Unauthorized verification attempt: ${normalizedEmail}`);
        return res.status(403).json({
            success: false,
            error: 'ACCESS DENIED'
        });
    }

    // Check if code has expired
    if (!isCodeValid()) {
        console.log(`⏰ Code expired for: ${normalizedEmail}`);
        return res.status(400).json({
            success: false,
            error: 'CODE_EXPIRED',
            message: 'Security code has expired. A new code has been sent to your email.'
        });
    }

    // Verify code
    if (code !== currentSecurityCode) {
        console.log(`❌ Invalid code attempt from: ${normalizedEmail}`);
        return res.status(400).json({
            success: false,
            error: 'INVALID_CODE',
            message: 'Invalid security code. Please check your email for the correct code.'
        });
    }

    console.log(`🎉 ACCESS GRANTED: ${normalizedEmail}`);

    // Generate session token
    const sessionToken = crypto.randomBytes(32).toString('hex');

    res.json({
        success: true,
        message: 'Access granted',
        token: sessionToken,
        user: {
            email: normalizedEmail,
            role: 'enterprise_user',
            permissions: ['read', 'analyze', 'export']
        }
    });
});

// Get access logs (for security dashboard)
app.get('/api/auth/logs', (req, res) => {
    res.json({
        logs: accessLogs.slice(-50), // Last 50 logs
        currentCodeExpiry: codeGeneratedAt + CODE_VALIDITY_MS,
        authorizedUsers: AUTHORIZED_EMAILS.length
    });
});

// Get code status (for admin)
app.get('/api/auth/status', (req, res) => {
    const timeLeft = getTimeUntilRotation();
    res.json({
        codeValid: isCodeValid(),
        expiresIn: timeLeft,
        authorizedEmails: AUTHORIZED_EMAILS,
        totalAccessAttempts: accessLogs.length
    });
});

// ==================== SERVER STARTUP ====================

const PORT = process.env.AUTH_PORT || 3001;

app.listen(PORT, () => {
    console.log('\n' + '='.repeat(60));
    console.log('🛡️  JARVIS ENTERPRISE SECURITY SERVER');
    console.log('='.repeat(60));
    console.log(`\n📍 Running on: http://localhost:${PORT}`);
    console.log('\n👥 Authorized Users:');
    AUTHORIZED_EMAILS.forEach((email, i) => {
        console.log(`   ${i + 1}. ${email}`);
    });

    // Generate initial code
    rotateSecurityCode();

    // Set up hourly code rotation
    setInterval(() => {
        console.log('\n⏰ Code rotation triggered...');
        rotateSecurityCode();
    }, CODE_VALIDITY_MS);

    console.log('\n✅ Server ready. Security codes rotate every hour.');
    console.log('='.repeat(60) + '\n');
});
