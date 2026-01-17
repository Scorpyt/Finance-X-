import math
import random
from datetime import datetime, timedelta
from typing import List, Dict, Tuple, Optional
from models import MarketEvent, ProcessedEvent, SystemState, MarketSnapshot, Ticker, PricePoint, MarketRegime, StudyCategory, QuestionDifficulty, InterviewQuestion, StudyTopic, StudyProgress, MarketScenario

class TechnicalAnalysis:
    @staticmethod
    def calculate_bollinger_bands(history: List[PricePoint], window: int = 20, num_std: float = 2.0) -> Tuple[List[float], List[float], List[float]]:
        """Returns (Upper Band, Middle Band, Lower Band)"""
        prices = [p.price for p in history]
        upper, middle, lower = [], [], []
        
        for i in range(len(prices)):
            if i < window - 1:
                # Not enough data
                upper.append(prices[i])
                middle.append(prices[i])
                lower.append(prices[i])
            else:
                slice_data = prices[i-window+1 : i+1]
                avg = sum(slice_data) / window
                variance = sum((x - avg) ** 2 for x in slice_data) / window
                std_dev = math.sqrt(variance)
                
                middle.append(avg)
                upper.append(avg + (std_dev * num_std))
                lower.append(avg - (std_dev * num_std))
        
        return upper, middle, lower

    @staticmethod
    def analyze_risk_depth(ticker: Ticker) -> Dict:
        """Analyzes price position relative to bands to determine Risk Depth."""
        if len(ticker.history) < 20:
             return {"depth": "LOW", "advice": "INSUFFICIENT DATA", "bid": 0.0}

        u, m, l = TechnicalAnalysis.calculate_bollinger_bands(ticker.history)
        current_price = ticker.current_price
        upper_curr = u[-1]
        lower_curr = l[-1]
        
        # Depth Logic
        if current_price > upper_curr:
             depth = "CRITICAL (OVERBOUGHT)"
             advice = "SELL / HEDGE"
             best_bid = lower_curr # Target return to mean or lower
        elif current_price < lower_curr:
             depth = "OPPORTUNITY (OVERSOLD)"
             advice = "ACCUMULATE"
             best_bid = current_price * 0.98 # Aggressive Bid
        else:
             depth = "NEUTRAL"
             advice = "HOLD"
             best_bid = lower_curr 
             
        return {
            "depth": depth,
            "advice": advice,
            "bid": best_bid,
            "volatility": (upper_curr - lower_curr) / m[-1]
        }

class StudyInsights:
    """Finance interview preparation system with real-time market data integration."""
    
    def __init__(self):
        self.topics: Dict[str, StudyTopic] = {}
        self.questions: List[InterviewQuestion] = []
        self.progress: Dict[str, StudyProgress] = {}
        self.current_scenario: Optional[MarketScenario] = None
        self._init_topics()
        self._init_questions()
    
    def _init_topics(self):
        """Initialize study topics for each category."""
        topics_data = [
            ("ib_valuation", "Valuation Methods", StudyCategory.INVESTMENT_BANKING, 
             "DCF, Comparable Companies, Precedent Transactions", 15,
             ["Rosenbaum & Pearl - Investment Banking", "Damodaran - Valuation"]),
            ("ib_ma", "M&A Analysis", StudyCategory.INVESTMENT_BANKING,
             "Merger models, accretion/dilution, synergies", 12,
             ["DePamphilis - Mergers and Acquisitions"]),
            ("pe_lbo", "LBO Modeling", StudyCategory.PRIVATE_EQUITY,
             "Leveraged buyout mechanics, returns analysis", 10,
             ["Private Equity at Work", "Pignataro - Financial Modeling"]),
            ("pe_due_diligence", "Due Diligence", StudyCategory.PRIVATE_EQUITY,
             "Financial, commercial, and operational DD", 8,
             ["Private Equity Operational Due Diligence"]),
            ("hf_strategies", "Trading Strategies", StudyCategory.HEDGE_FUNDS,
             "Long/short equity, event-driven, macro", 12,
             ["More Money Than God", "The Alpha Masters"]),
            ("hf_risk", "Risk Management", StudyCategory.HEDGE_FUNDS,
             "VaR, Greeks, position sizing, hedging", 10,
             ["Options as a Strategic Investment"]),
            ("am_portfolio", "Portfolio Theory", StudyCategory.ASSET_MANAGEMENT,
             "MPT, CAPM, factor models, optimization", 12,
             ["CFA Level III Curriculum", "Active Portfolio Management"]),
            ("am_performance", "Performance Attribution", StudyCategory.ASSET_MANAGEMENT,
             "Brinson analysis, risk-adjusted returns", 8,
             ["GIPS Standards"]),
            ("fa_statements", "Financial Statements", StudyCategory.FINANCIAL_ANALYSIS,
             "Income statement, balance sheet, cash flow analysis", 15,
             ["Financial Intelligence", "Warren Buffett's Balance Sheet"]),
            ("fa_ratios", "Financial Ratios", StudyCategory.FINANCIAL_ANALYSIS,
             "Profitability, liquidity, leverage, efficiency", 12,
             ["Financial Statement Analysis", "The Interpretation of Financial Statements"])
        ]
        
        for tid, name, cat, desc, qcount, resources in topics_data:
            self.topics[tid] = StudyTopic(
                id=tid, name=name, category=cat, description=desc,
                questions_count=qcount, resources=resources
            )
    
    def _init_questions(self):
        """Initialize interview question bank."""
        questions_data = [
            # Investment Banking - Valuation
            ("q_dcf_1", StudyCategory.INVESTMENT_BANKING, QuestionDifficulty.INTERMEDIATE,
             "Walk me through a DCF analysis.",
             "Project free cash flows, calculate terminal value, discount to present value using WACC.",
             "A DCF values a company based on the present value of its future cash flows. Key steps: 1) Project revenue and expenses, 2) Calculate unlevered FCF, 3) Determine terminal value (perpetuity or exit multiple), 4) Discount using WACC, 5) Add non-operating assets and subtract debt for equity value.",
             False, ["ib_valuation"]),
            ("q_wacc_1", StudyCategory.INVESTMENT_BANKING, QuestionDifficulty.INTERMEDIATE,
             "How do you calculate WACC and what factors affect it?",
             "WACC = (E/V × Re) + (D/V × Rd × (1-T)). Affected by capital structure, beta, risk-free rate, and tax rate.",
             "WACC represents the blended cost of capital. Cost of equity typically uses CAPM: Rf + β(Rm-Rf). Cost of debt is the yield on the company's debt. Higher leverage increases equity risk but debt is tax-deductible.",
             False, ["ib_valuation"]),
            ("q_ev_1", StudyCategory.INVESTMENT_BANKING, QuestionDifficulty.BEGINNER,
             "What is Enterprise Value and how do you calculate it?",
             "EV = Market Cap + Debt + Preferred Stock + Minority Interest - Cash.",
             "EV represents the total value to acquire a business. You add debt because an acquirer assumes it, and subtract cash because it reduces the net purchase price. EV is capital structure neutral.",
             True, ["ib_valuation"]),
            # Private Equity - LBO
            ("q_lbo_1", StudyCategory.PRIVATE_EQUITY, QuestionDifficulty.ADVANCED,
             "What drives returns in an LBO? Walk through the sources of value creation.",
             "Returns come from: 1) EBITDA growth, 2) Multiple expansion, 3) Debt paydown.",
             "PE firms create value through operational improvements (revenue growth, margin expansion), financial engineering (optimal leverage, debt paydown), and multiple arbitrage (buying low, selling high). Debt paydown is often the most reliable source.",
             False, ["pe_lbo"]),
            ("q_irr_1", StudyCategory.PRIVATE_EQUITY, QuestionDifficulty.INTERMEDIATE,
             "A PE firm buys a company for $100M with 60% debt. After 5 years, they sell for $200M. What's the approximate equity IRR?",
             "Equity invested: $40M. Exit equity: $200M - remaining debt. IRR around 35-40% depending on debt paydown.",
             "Equity check = $40M. If debt is fully paid, exit equity = $200M. MOIC = 5x. Using rule of 72, 5x in 5 years ≈ 38% IRR. Leverage amplifies returns when the investment performs well.",
             False, ["pe_lbo"]),
            # Hedge Funds - Strategies
            ("q_ls_1", StudyCategory.HEDGE_FUNDS, QuestionDifficulty.INTERMEDIATE,
             "Explain a long/short equity strategy and how it manages risk.",
             "Long undervalued stocks, short overvalued ones. Hedges market risk while profiting from stock selection.",
             "L/S equity aims to generate alpha through stock picking while reducing market (beta) exposure. Net exposure = Long - Short. A 130/30 fund is 130% long, 30% short (100% net). Reduces drawdowns in bear markets.",
             True, ["hf_strategies"]),
            ("q_event_1", StudyCategory.HEDGE_FUNDS, QuestionDifficulty.ADVANCED,
             "How would you trade an M&A announcement? What are the risks?",
             "Merger arb: Long target, short acquirer (in stock deals). Risks: deal break, regulatory issues, financing.",
             "After announcement, target trades below deal price (deal spread). Arb captures spread at close. Key risks: antitrust block, financing failure, due diligence issues, MAC clauses. Size position for deal break risk.",
             True, ["hf_strategies"]),
            # Asset Management - Portfolio Theory
            ("q_sharpe_1", StudyCategory.ASSET_MANAGEMENT, QuestionDifficulty.BEGINNER,
             "What is the Sharpe Ratio and why is it important?",
             "Sharpe = (Return - Risk-free Rate) / Standard Deviation. Measures risk-adjusted returns.",
             "Sharpe ratio tells you how much excess return you're getting per unit of risk. Higher is better. A Sharpe of 1.0 is good, 2.0 is excellent. Limitations: assumes normal returns, uses standard deviation (penalizes upside).",
             True, ["am_portfolio"]),
            # Financial Analysis
            ("q_fcf_1", StudyCategory.FINANCIAL_ANALYSIS, QuestionDifficulty.INTERMEDIATE,
             "How do you calculate Free Cash Flow and why does it matter?",
             "FCF = Operating Cash Flow - CapEx. Shows cash available after maintaining operations.",
             "FCF is the cash a company generates after accounting for capital investments. It's crucial for: 1) Valuation (DCF uses FCF), 2) Dividend capacity, 3) Debt repayment ability, 4) M&A firepower. Positive FCF indicates financial health.",
             False, ["fa_statements"]),
            ("q_ratio_1", StudyCategory.FINANCIAL_ANALYSIS, QuestionDifficulty.BEGINNER,
             "What are the key profitability ratios and what do they tell you?",
             "Gross margin, operating margin, net margin, ROE, ROA, ROIC.",
             "Gross margin shows production efficiency. Operating margin indicates operational efficiency. Net margin is bottom-line profitability. ROE measures return to shareholders. ROIC shows how well capital is deployed regardless of financing.",
             True, ["fa_ratios"])
        ]
        
        for qid, cat, diff, q, a, exp, uses_data, topics in questions_data:
            self.questions.append(InterviewQuestion(
                id=qid, category=cat, difficulty=diff, question=q,
                answer=a, explanation=exp, uses_market_data=uses_data, related_topics=topics
            ))
    
    def get_topics_by_category(self, category: StudyCategory) -> List[StudyTopic]:
        """Get all topics for a specific category."""
        return [t for t in self.topics.values() if t.category == category]
    
    def get_all_topics(self) -> List[Dict]:
        """Get all topics as dictionaries for API response."""
        return [
            {
                "id": t.id,
                "name": t.name,
                "category": t.category.value,
                "description": t.description,
                "questions_count": t.questions_count,
                "resources": t.resources
            }
            for t in self.topics.values()
        ]
    
    def get_questions_by_category(self, category: str) -> List[Dict]:
        """Get questions for a specific category."""
        try:
            cat = StudyCategory(category)
            questions = [q for q in self.questions if q.category == cat]
        except ValueError:
            questions = self.questions[:5]  # Default to first 5
        
        return [
            {
                "id": q.id,
                "category": q.category.value,
                "difficulty": q.difficulty.value,
                "question": q.question,
                "uses_market_data": q.uses_market_data
            }
            for q in questions
        ]
    
    def get_question_with_answer(self, question_id: str) -> Optional[Dict]:
        """Get a specific question with its answer and explanation."""
        for q in self.questions:
            if q.id == question_id:
                return {
                    "id": q.id,
                    "category": q.category.value,
                    "difficulty": q.difficulty.value,
                    "question": q.question,
                    "answer": q.answer,
                    "explanation": q.explanation,
                    "related_topics": q.related_topics
                }
        return None
    
    def generate_market_scenario(self, market_data: Dict) -> Dict:
        """Generate a real-time market scenario based on current data."""
        vix = market_data.get("VIX", 15)
        spx = market_data.get("SPX", 4800)
        btc = market_data.get("BTC", 42000)
        
        if vix > 25:
            scenario_type = "high_volatility"
            title = "Market Stress Scenario"
            description = f"VIX has spiked to {vix:.1f}, indicating elevated fear in the market."
            challenge = f"The S&P 500 is at {spx:,.0f} and volatility is elevated. As a portfolio manager with a $100M equity portfolio, what hedging strategies would you implement?"
            hints = [
                "Consider protective puts or put spreads",
                "Think about VIX calls as tail-risk hedge",
                "Evaluate reducing gross exposure"
            ]
            solution = "In high vol environments: 1) Buy SPX puts 5-10% OTM, 2) Consider VIX call spreads, 3) Reduce net exposure to 70-80%, 4) Trim high-beta positions."
        elif vix < 12:
            scenario_type = "low_volatility"
            title = "Complacency Warning"
            description = f"VIX at {vix:.1f} suggests market complacency. Historically, this precedes volatility spikes."
            challenge = "With volatility near historic lows, how would you position a portfolio to protect against a potential vol spike while minimizing cost?"
            hints = [
                "Options are cheap - consider buying protection",
                "Look at put ratios or calendars",
                "VIX products are attractively priced"
            ]
            solution = "When vol is cheap: 1) Establish put protection at low cost, 2) Buy VIX calls 3-6 months out, 3) Consider tail-risk strategies, 4) Collar positions to lock in gains."
        else:
            scenario_type = "normal_market"
            title = "Equity Valuation Exercise"
            description = f"With S&P 500 at {spx:,.0f} and BTC at ${btc:,.0f}, analyze relative valuations."
            challenge = f"A tech company trades at 25x forward P/E. The S&P 500 forward P/E is approximately {spx/195:.1f}x. Is the premium justified? What additional analysis would you perform?"
            hints = [
                "Compare growth rates to justify multiple",
                "Consider PEG ratio analysis",
                "Evaluate margin trajectory"
            ]
            solution = "Premium analysis: 1) Calculate PEG ratios, 2) Compare revenue growth rates, 3) Assess margin expansion potential, 4) Evaluate competitive moat, 5) Model DCF to validate."
        
        return {
            "type": scenario_type,
            "title": title,
            "description": description,
            "challenge": challenge,
            "hints": hints,
            "solution_approach": solution,
            "market_context": {
                "VIX": vix,
                "SPX": spx,
                "BTC": btc
            }
        }
    
    def get_resources(self, category: Optional[str] = None) -> List[Dict]:
        """Get study resources, optionally filtered by category."""
        resources = [
            # Investment Banking
            {
                "category": "investment_banking",
                "title": "Investment Banking: Valuation, LBOs, M&A",
                "author": "Rosenbaum & Pearl",
                "type": "book",
                "description": "The definitive guide to IB technical skills"
            },
            {
                "category": "investment_banking",
                "title": "Breaking Into Wall Street",
                "author": "BIWS",
                "type": "course",
                "description": "Financial modeling and interview prep"
            },
            {
                "category": "investment_banking",
                "title": "Valuation: Measuring and Managing Value",
                "author": "McKinsey & Company",
                "type": "book",
                "description": "Comprehensive valuation framework"
            },
            {
                "category": "investment_banking",
                "title": "Wall Street Prep",
                "author": "WSP",
                "type": "course",
                "description": "Excel modeling and IB training"
            },
            # Private Equity
            {
                "category": "private_equity",
                "title": "Private Equity at Work",
                "author": "Appelbaum & Batt",
                "type": "book",
                "description": "Understanding PE mechanics and impact"
            },
            {
                "category": "private_equity",
                "title": "Mastering Private Equity",
                "author": "Zeisberger, Prahl & White",
                "type": "book",
                "description": "Transformation via venture capital and buyouts"
            },
            {
                "category": "private_equity",
                "title": "The Private Equity Playbook",
                "author": "Adam Coffey",
                "type": "book",
                "description": "Management's guide to working with PE"
            },
            # Hedge Funds
            {
                "category": "hedge_funds",
                "title": "More Money Than God",
                "author": "Sebastian Mallaby",
                "type": "book",
                "description": "History of hedge funds and strategies"
            },
            {
                "category": "hedge_funds",
                "title": "The Alpha Masters",
                "author": "Maneet Ahuja",
                "type": "book",
                "description": "Unlocking the genius of world's top hedge funds"
            },
            {
                "category": "hedge_funds",
                "title": "Hedge Fund Market Wizards",
                "author": "Jack Schwager",
                "type": "book",
                "description": "Interviews with successful hedge fund traders"
            },
            {
                "category": "hedge_funds",
                "title": "Options as a Strategic Investment",
                "author": "Lawrence McMillan",
                "type": "book",
                "description": "Comprehensive options trading strategies"
            },
            # Asset Management
            {
                "category": "asset_management",
                "title": "CFA Program",
                "author": "CFA Institute",
                "type": "certification",
                "description": "Gold standard for investment professionals"
            },
            {
                "category": "asset_management",
                "title": "Active Portfolio Management",
                "author": "Grinold & Kahn",
                "type": "book",
                "description": "Quantitative theory and applications"
            },
            {
                "category": "asset_management",
                "title": "Expected Returns",
                "author": "Antti Ilmanen",
                "type": "book",
                "description": "Investor's guide to harvesting market rewards"
            },
            {
                "category": "asset_management",
                "title": "CAIA Charter",
                "author": "CAIA Association",
                "type": "certification",
                "description": "Alternative investment professional designation"
            },
            # Financial Analysis
            {
                "category": "financial_analysis",
                "title": "Financial Intelligence",
                "author": "Berman & Knight",
                "type": "book",
                "description": "Understanding financial statements"
            },
            {
                "category": "financial_analysis",
                "title": "Financial Statement Analysis",
                "author": "Martin Fridson",
                "type": "book",
                "description": "Practitioner's guide to analyzing financials"
            },
            {
                "category": "financial_analysis",
                "title": "The Interpretation of Financial Statements",
                "author": "Benjamin Graham",
                "type": "book",
                "description": "Classic guide by the father of value investing"
            },
            {
                "category": "financial_analysis",
                "title": "Damodaran on Valuation",
                "author": "Aswath Damodaran",
                "type": "book",
                "description": "Security analysis for investment and corporate finance"
            },
            # General Resources
            {
                "category": "general",
                "title": "Wall Street Oasis",
                "author": "WSO Community",
                "type": "website",
                "description": "Finance career forum and interview guides"
            },
            {
                "category": "general",
                "title": "Mergers & Inquisitions",
                "author": "M&I",
                "type": "website",
                "description": "Investment banking interview prep"
            },
            {
                "category": "general",
                "title": "QuantNet",
                "author": "QuantNet",
                "type": "website",
                "description": "Quantitative finance community and resources"
            }
        ]
        
        if category:
            return [r for r in resources if r["category"] == category]
        return resources

class MarketSimulator:
    def __init__(self):
        self.tickers: Dict[str, Ticker] = {
            "SPX": Ticker("SPX", "S&P 500", 4800.0, 0.0),
            "NDX": Ticker("NDX", "Nasdaq 100", 16800.0, 0.0),
            "BTC": Ticker("BTC", "Bitcoin", 42000.0, 0.0),
            "VIX": Ticker("VIX", "Volatility", 14.0, 0.0),
            "AAPL": Ticker("AAPL", "Apple Inc.", 185.0, 0.0, sector="TECH"),
            "NVDA": Ticker("NVDA", "NVIDIA", 550.0, 0.0, sector="TECH"),
            "JPM": Ticker("JPM", "JPMorgan", 170.0, 0.0, sector="FINANCE"),
            "XOM": Ticker("XOM", "Exxon Mobil", 100.0, 0.0, sector="ENERGY"),
            "WTI": Ticker("WTI", "Crude Oil (WTI)", 72.50, 0.0, sector="ENERGY"),
            "BRENT": Ticker("BRENT", "Crude Oil (Brent)", 77.80, 0.0, sector="ENERGY")
        }
        start_time = datetime(2024, 1, 1, 9, 0)
        for t in self.tickers.values():
            t.history.append(PricePoint(start_time, t.current_price, 0))

    def update_prices(self, current_time: datetime, system_risk: float):
        bias = 0.0
        volatility_multiplier = 1.0

        if system_risk > 25.0: # CRASH
            bias = -0.02
            volatility_multiplier = 4.0
        elif system_risk > 15.0: # HIGH VOL
            bias = -0.005
            volatility_multiplier = 2.0
        elif system_risk < 5.0: # STABLE
            bias = 0.001
            volatility_multiplier = 0.8

        for sym, ticker in self.tickers.items():
            base_vol = 0.002 if sym != "VIX" else 0.05
            if sym == "BTC": base_vol = 0.01
            if sym in ["WTI", "BRENT"]: base_vol = 0.008

            shock = random.gauss(0, base_vol * volatility_multiplier)
            if sym == "VIX":
                change_pct = shock - (bias * 5)
            else:
                change_pct = shock + bias

            new_price = ticker.current_price * (1 + change_pct)
            ticker.current_price = round(new_price, 2)
            volume = int(random.uniform(1000, 5000) * volatility_multiplier)
            
            ticker.history.append(PricePoint(current_time, ticker.current_price, volume))
            if len(ticker.history) > 100:
                ticker.history.pop(0)

            ticker.change_pct = ((ticker.current_price - ticker.history[0].price) / ticker.history[0].price) * 100

class IntelligenceEngine:
    def __init__(self, decay_rate: float = 0.1):
        self.events: List[ProcessedEvent] = []
        self.decay_rate = decay_rate
        self.current_state = SystemState.STABLE
        self.current_regime = MarketRegime.LOW_VOL
        self.simulator = MarketSimulator()
        self.study_insights = StudyInsights()

    def ingest(self, event: MarketEvent):
        relevance = event.base_impact * 1.0 
        processed = ProcessedEvent(
            original_event=event,
            current_weight=relevance,
            relevance_score=relevance
        )
        self.events.append(processed)
        print(f"[{event.timestamp.strftime('%H:%M:%S')}] Ingested: {event.description} (Impact: {event.base_impact})")

    def apply_decay(self, current_time: datetime):
        active_events = []
        for p_event in self.events:
            time_delta = (current_time - p_event.original_event.timestamp).total_seconds() / 3600.0 # Hours
            new_weight = p_event.relevance_score * math.exp(-self.decay_rate * time_delta)
            p_event.current_weight = new_weight
            if new_weight > 0.5:
                active_events.append(p_event)
        self.events = active_events

    def detect_state(self, current_time: datetime) -> MarketSnapshot:
        total_risk = sum(e.current_weight for e in self.events)
        
        if total_risk > 25.0:
            self.current_state = SystemState.CRASH
            self.current_regime = MarketRegime.HIGH_VOL
        elif total_risk > 15.0:
            self.current_state = SystemState.HIGH_VOLATILITY
            self.current_regime = MarketRegime.HIGH_VOL
        elif total_risk < 5.0:
            self.current_state = SystemState.STABLE
            self.current_regime = MarketRegime.LOW_VOL
            
        self.simulator.update_prices(current_time, total_risk)

        top_events = sorted(self.events, key=lambda x: x.current_weight, reverse=True)[:5]
        
        return MarketSnapshot(
            timestamp=current_time,
            state=self.current_state,
            risk_score=round(total_risk, 2),
            active_events=top_events,
            regime=self.current_regime
        )
            
    def get_ticker(self, symbol: str) -> Ticker:
        return self.simulator.tickers.get(symbol)
    
    def get_all_tickers(self) -> List[Dict]:
        return [
            {
                "symbol": t.symbol,
                "price": t.current_price,
                "change": t.change_pct,
                "sector": t.sector
            }
            for t in self.simulator.tickers.values()
        ]
