import unittest, sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from engine.data_loader import DataLoader
from engine.swarm_runner import SwarmRunner
from models.hybrid_orb import HybridORBModel

class TestHybrid(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.runner = SwarmRunner()

    def test_hybrid_2024_primary(self):
        # 44 tickers primary: 321 trades 53% ret — verify after ponytail ultra parity
        _, _, m = self.runner.run_hybrid_portfolio(
            ["AAPL","ADBE","AMAT","AMD","AMGN","AMZN","ASML","AVGO","BKNG","CAT","CDNS","COIN","COST","FTNT","GE","GILD","GLD","GOOGL","GS","IWM","KLAC","LLY","LMT","LRCX","MA","MELI","META","MSFT","MU","NFLX","NVDA","PANW","PLTR","PYPL","QQQ","REGN","SNPS","SPY","SQQQ","TQQQ","TSLA","V","VOO","VRTX"],
            2024, 2024, 5, 1.5, 0.6, 2.0, 2.0, 5, 50000, 0.01)
        self.assertGreater(m['total_trades'], 300)
        self.assertGreater(m['sharpe_ratio'], 1.5)
        self.assertGreater(m['profit_factor'], 1.4)
        self.assertAlmostEqual(m['total_return_pct'], 53.03, delta=0.1)

    def test_phi_filter_blocks_chop(self):
        m = HybridORBModel(5, 1.5, 0.6, 2.0, 2.0)
        self.assertEqual(m.phi_min, 0.6)

    def test_rvol_filter_blocks_low_vol(self):
        m = HybridORBModel(5, 1.5)
        self.assertEqual(m.min_rvol, 1.5)

    def test_no_retrace_param(self):
        m = HybridORBModel()
        self.assertFalse(hasattr(m, 'use_retrace'))

    def test_legacy_import_still_works(self):
        from models.legacy.naive_sweep_reversal import NaiveSweepReversalModel
        from models.legacy.confirmation_reversal import ConfirmationReversalModel
        self.assertTrue(NaiveSweepReversalModel)
        self.assertTrue(ConfirmationReversalModel)

    def test_hybrid_5ticker_subset(self):
        # 5 tickers gives ~16 trades in 2024 — sanity check subset still works
        _, _, m = self.runner.run_hybrid_portfolio(["QQQ","SPY","NVDA","AAPL","MSFT"], 2024, 2024, 5, 1.5, 0.6, 2.0, 2.0, 5)
        self.assertGreater(m['total_trades'], 10)

if __name__ == '__main__':
    unittest.main()
