"""
This is a copy of the OptionStrategySystem module so that the Vercel
serverless function can import it without dependency on external files.  See
the root-level option_strategy_system.py for the full documentation.  This
version is identical to the original at the time of project creation.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import List, Dict, Any, Optional


class DataEngine:
    def __init__(self):
        # Read API credentials from environment variables.  Set these in Vercel
        # under Project Settings → Environment Variables.
        import os
        self.finnhub_api_key = os.environ.get('FINNHUB_API_KEY')
        self.ibkr_client_id = os.environ.get('IBKR_CLIENT_ID')
        self.ibkr_api_key = os.environ.get('IBKR_API_KEY')

        self._price_cache: Dict[str, float] = {}
        self._option_chain_cache: Dict[str, List[Dict[str, Any]]] = {}
        self._historical_cache: Dict[str, Any] = {}

    def fetch_current_positions(self) -> List[Dict[str, Any]]:
        return []

    def fetch_option_chain(self, symbol: str, expiry: Optional[str] = None) -> List[Dict[str, Any]]:
        return []

    def fetch_real_time_price(self, symbol: str) -> float:
        return 0.0

    def fetch_historical_prices(self, symbol: str, period: str = '1y', interval: str = '1d') -> Any:
        return None


class RegimeEngine:
    def __init__(self, data_engine: DataEngine):
        self.data_engine = data_engine

    def evaluate_regime(self, symbol: str) -> Dict[str, str]:
        return {'trend': 'neutral', 'volatility': 'neutral', 'skew': 'neutral'}


class PositioningProxyEngine:
    def __init__(self, data_engine: DataEngine):
        self.data_engine = data_engine

    def compute_proxies(self, symbol: str) -> Dict[str, Any]:
        return {'oi_density': 0.0, 'skew_level': 0.0, 'term_slope': 0.0}


@dataclass
class StrategyCandidate:
    name: str
    legs: List[Dict[str, Any]]
    objective: str
    notes: Optional[str] = None


class StrategyRouter:
    def route(self, symbol: str, regime: Dict[str, str], objective: str) -> List[StrategyCandidate]:
        candidates: List[StrategyCandidate] = []
        trend = regime.get('trend', 'neutral')
        vol = regime.get('volatility', 'neutral')
        if objective == 'income':
            if vol in ['high', 'elevated']:
                candidates.append(StrategyCandidate(
                    name='Iron Condor',
                    legs=[
                        {'type': 'put', 'direction': 'short', 'strike_offset': -0.1},
                        {'type': 'put', 'direction': 'long', 'strike_offset': -0.2},
                        {'type': 'call', 'direction': 'short', 'strike_offset': 0.1},
                        {'type': 'call', 'direction': 'long', 'strike_offset': 0.2},
                    ],
                    objective=objective,
                    notes='High IV; short premium collected'
                ))
            else:
                candidates.append(StrategyCandidate(
                    name='Put Calendar Spread',
                    legs=[
                        {'type': 'put', 'direction': 'long', 'expiry_offset': 2},
                        {'type': 'put', 'direction': 'short', 'expiry_offset': 1},
                    ],
                    objective=objective,
                    notes='Low IV; collect theta while owning vega'
                ))
        elif objective == 'trend':
            if trend in ['bull', 'up']:
                candidates.append(StrategyCandidate(
                    name='Call Debit Spread',
                    legs=[
                        {'type': 'call', 'direction': 'long', 'strike_offset': 0.0},
                        {'type': 'call', 'direction': 'short', 'strike_offset': 0.05},
                    ],
                    objective=objective,
                    notes='Directional play with limited risk'
                ))
                candidates.append(StrategyCandidate(
                    name='PMCC',
                    legs=[
                        {'type': 'stock', 'direction': 'long', 'quantity': 100},
                        {'type': 'call', 'direction': 'short', 'strike_offset': 0.1, 'expiry_offset': 1},
                    ],
                    objective=objective,
                    notes='Poor man covered call: synthetic long stock with call income'
                ))
            elif trend in ['bear', 'down']:
                candidates.append(StrategyCandidate(
                    name='Put Debit Spread',
                    legs=[
                        {'type': 'put', 'direction': 'long', 'strike_offset': 0.0},
                        {'type': 'put', 'direction': 'short', 'strike_offset': -0.05},
                    ],
                    objective=objective,
                    notes='Bearish directional play'
                ))
        elif objective == 'volatility':
            if vol in ['low', 'neutral']:
                candidates.append(StrategyCandidate(
                    name='Long Straddle',
                    legs=[
                        {'type': 'call', 'direction': 'long', 'strike_offset': 0.0},
                        {'type': 'put', 'direction': 'long', 'strike_offset': 0.0},
                    ],
                    objective=objective,
                    notes='Expecting volatility expansion'
                ))
            elif vol in ['high', 'elevated']:
                candidates.append(StrategyCandidate(
                    name='Iron Fly',
                    legs=[
                        {'type': 'call', 'direction': 'short', 'strike_offset': 0.0},
                        {'type': 'call', 'direction': 'long', 'strike_offset': 0.1},
                        {'type': 'put', 'direction': 'short', 'strike_offset': 0.0},
                        {'type': 'put', 'direction': 'long', 'strike_offset': -0.1},
                    ],
                    objective=objective,
                    notes='Short volatility structure with limited risk'
                ))
        return candidates


class ScoreEngine:
    def __init__(self, data_engine: DataEngine):
        self.data_engine = data_engine

    def score(self, candidates: List[StrategyCandidate], objective: str) -> List[Dict[str, Any]]:
        scored_list: List[Dict[str, Any]] = []
        for candidate in candidates:
            score = 0.5
            scored_list.append({'candidate': candidate, 'score': score})
        scored_list.sort(key=lambda x: x['score'], reverse=True)
        return scored_list


class OptionStrategySystem:
    def __init__(self):
        self.data_engine = DataEngine()
        self.regime_engine = RegimeEngine(self.data_engine)
        self.positioning_engine = PositioningProxyEngine(self.data_engine)
        self.strategy_router = StrategyRouter()
        self.score_engine = ScoreEngine(self.data_engine)

    def get_best_strategy(self, symbol: str, objective: str) -> Dict[str, Any]:
        regime = self.regime_engine.evaluate_regime(symbol)
        candidates = self.strategy_router.route(symbol, regime, objective)
        scored = self.score_engine.score(candidates, objective)
        return scored[0] if scored else {}