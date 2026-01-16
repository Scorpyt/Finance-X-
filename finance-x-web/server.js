const express = require('express');
const cors = require('cors');
const axios = require('axios');
const path = require('path');

const app = express();
const PORT = process.env.PORT || 3000;
const BACKEND_URL = 'http://localhost:8000'; // Python FastAPI backend

// Middleware
app.use(cors());
app.use(express.json());
app.use(express.static('public'));

// Proxy endpoint to Python backend
app.post('/api/command', async (req, res) => {
    try {
        const response = await axios.post(`${BACKEND_URL}/command`, req.body);
        res.json(response.data);
    } catch (error) {
        console.error('Backend error:', error.message);
        res.status(500).json({
            type: 'ERROR',
            content: 'Backend connection failed. Ensure Python server is running on port 8000.'
        });
    }
});

// Serve landing page
app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, 'public', 'index.html'));
});

// Serve ordinary mode
app.get('/ordinary', (req, res) => {
    res.sendFile(path.join(__dirname, 'public', 'ordinary.html'));
});

// Serve enterprise mode
app.get('/enterprise', (req, res) => {
    res.sendFile(path.join(__dirname, 'public', 'enterprise.html'));
});

// Health check
app.get('/health', (req, res) => {
    res.json({ status: 'ok', mode: 'Node.js Frontend Server' });
});

app.listen(PORT, () => {
    console.log(`
╔═══════════════════════════════════════════════════════╗
║                                                       ║
║           FINANCE-X WEB SERVER STARTED                ║
║                                                       ║
║   🌐 Frontend:  http://localhost:${PORT}              ║
║   🔧 Backend:   ${BACKEND_URL}                        ║
║                                                       ║
║   📊 Ordinary Mode:   /ordinary                       ║
║   💼 Enterprise Mode: /enterprise                     ║
║                                                       ║
╚═══════════════════════════════════════════════════════╝
    `);
});
