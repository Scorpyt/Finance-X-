"""
Finance-X Web Terminal - Localhost Server
Beautiful web-based terminal for Indian stock market analysis
"""

from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
from india_engine import IndiaMarketEngine
from datetime import datetime
import threading

app = Flask(__name__)
CORS(app)

# Initialize India Market Engine
india_engine = IndiaMarketEngine(default_categories=['NIFTY_50', 'BANK', 'IT'])

@app.route('/')
def index():
    """Main terminal page"""
    return render_template('terminal.html')

@app.route('/api/stats')
def get_stats():
    """Get coverage statistics"""
    try:
        stats = india_engine.get_coverage_stats()
        return jsonify({'success': True, 'data': stats})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/nifty50')
def get_nifty50():
    """Get NIFTY 50 stocks"""
    try:
        data = india_engine.fetch_market_snapshot(categories=['NIFTY_50'])
        return jsonify({'success': True, 'data': data, 'count': len(data)})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/sector/<sector>')
def get_sector(sector):
    """Get sector stocks"""
    try:
        data = india_engine.get_sector_stocks(sector.upper())
        return jsonify({'success': True, 'sector': sector.upper(), 'data': data, 'count': len(data)})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/search')
def search_stocks():
    """Search stocks"""
    try:
        query = request.args.get('q', '')
        matches = india_engine.search_stocks(query)
        return jsonify({'success': True, 'query': query, 'data': matches, 'count': len(matches)})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/summary')
def get_summary():
    """Get market summary"""
    try:
        categories = request.args.get('categories', 'NIFTY_50,BANK,IT').split(',')
        summary = india_engine.get_category_summary(categories)
        return jsonify({'success': True, 'data': summary})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/top-movers')
def get_top_movers():
    """Get top movers"""
    try:
        category = request.args.get('category', None)
        top_n = int(request.args.get('top_n', 10))
        movers = india_engine.get_top_movers(category=category, top_n=top_n)
        return jsonify({'success': True, 'data': movers})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

if __name__ == '__main__':
    print("=" * 70)
    print("  FINANCE-X WEB TERMINAL")
    print("=" * 70)
    print("\n  >> Starting server...")
    print("\n  >> Open in browser: http://localhost:5000")
    print("  >> Coverage: 240+ Indian stocks")
    print("\n  Press Ctrl+C to stop")
    print("=" * 70)
    
    app.run(host='0.0.0.0', port=5000, debug=False)
