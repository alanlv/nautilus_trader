# -------------------------------------------------------------------------------------------------
#  Copyright (C) 2015-2022 Nautech Systems Pty Ltd. All rights reserved.
#  https://nautechsystems.io
#
#  Licensed under the GNU Lesser General Public License Version 3.0 (the "License");
#  You may not use this file except in compliance with the License.
#  You may obtain a copy of the License at https://www.gnu.org/licenses/lgpl-3.0.en.html
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
# -------------------------------------------------------------------------------------------------

import pathlib
from datetime import date
from decimal import Decimal
from typing import Optional

import fsspec
import pandas as pd
from fsspec.implementations.github import GithubFileSystem
from fsspec.implementations.local import LocalFileSystem

from nautilus_trader.adapters.betfair.common import BETFAIR_VENUE
from nautilus_trader.backtest.data.loaders import CSVBarDataLoader
from nautilus_trader.backtest.data.loaders import CSVTickDataLoader
from nautilus_trader.backtest.data.loaders import ParquetBarDataLoader
from nautilus_trader.backtest.data.loaders import ParquetTickDataLoader
from nautilus_trader.core.correctness import PyCondition
from nautilus_trader.model.currencies import ADA
from nautilus_trader.model.currencies import BTC
from nautilus_trader.model.currencies import ETH
from nautilus_trader.model.currencies import USD
from nautilus_trader.model.currencies import USDT
from nautilus_trader.model.currency import Currency
from nautilus_trader.model.enums import AssetClass
from nautilus_trader.model.enums import OptionKind
from nautilus_trader.model.identifiers import InstrumentId
from nautilus_trader.model.identifiers import Symbol
from nautilus_trader.model.identifiers import Venue
from nautilus_trader.model.instruments.betting import BettingInstrument
from nautilus_trader.model.instruments.crypto_future import CryptoFuture
from nautilus_trader.model.instruments.crypto_perpetual import CryptoPerpetual
from nautilus_trader.model.instruments.currency_pair import CurrencyPair
from nautilus_trader.model.instruments.equity import Equity
from nautilus_trader.model.instruments.future import Future
from nautilus_trader.model.instruments.option import Option
from nautilus_trader.model.objects import Money
from nautilus_trader.model.objects import Price
from nautilus_trader.model.objects import Quantity


class TestInstrumentProvider:
    """
    Provides instrument template methods for backtesting.
    """

    @staticmethod
    def adabtc_binance() -> CurrencyPair:
        """
        Return the Binance ADA/BTC instrument for backtesting.

        Returns
        -------
        CurrencyPair

        """
        return CurrencyPair(
            instrument_id=InstrumentId(
                symbol=Symbol("ADABTC"),
                venue=Venue("BINANCE"),
            ),
            native_symbol=Symbol("ADABTC"),
            base_currency=ADA,
            quote_currency=BTC,
            price_precision=8,
            size_precision=8,
            price_increment=Price(1e-08, precision=8),
            size_increment=Quantity(1e-08, precision=8),
            lot_size=None,
            max_quantity=Quantity.from_int(90000000),
            min_quantity=Quantity.from_int(1),
            max_notional=None,
            min_notional=Money(0.00010000, BTC),
            max_price=Price(1000, precision=8),
            min_price=Price(1e-8, precision=8),
            margin_init=Decimal("0"),
            margin_maint=Decimal("0"),
            maker_fee=Decimal("0.0010"),
            taker_fee=Decimal("0.0010"),
            ts_event=0,
            ts_init=0,
        )

    @staticmethod
    def btcusdt_binance() -> CurrencyPair:
        """
        Return the Binance BTCUSDT instrument for backtesting.

        Returns
        -------
        CurrencyPair

        """
        return CurrencyPair(
            instrument_id=InstrumentId(
                symbol=Symbol("BTCUSDT"),
                venue=Venue("BINANCE"),
            ),
            native_symbol=Symbol("BTCUSDT"),
            base_currency=BTC,
            quote_currency=USDT,
            price_precision=2,
            size_precision=6,
            price_increment=Price(1e-02, precision=2),
            size_increment=Quantity(1e-06, precision=6),
            lot_size=None,
            max_quantity=Quantity(9000, precision=6),
            min_quantity=Quantity(1e-06, precision=6),
            max_notional=None,
            min_notional=Money(10.00000000, USDT),
            max_price=Price(1000000, precision=2),
            min_price=Price(0.01, precision=2),
            margin_init=Decimal(0),
            margin_maint=Decimal(0),
            maker_fee=Decimal("0.001"),
            taker_fee=Decimal("0.001"),
            ts_event=0,
            ts_init=0,
        )

    @staticmethod
    def ethusdt_binance() -> CurrencyPair:
        """
        Return the Binance ETHUSDT instrument for backtesting.

        Returns
        -------
        CurrencyPair

        """
        return CurrencyPair(
            instrument_id=InstrumentId(
                symbol=Symbol("ETHUSDT"),
                venue=Venue("BINANCE"),
            ),
            native_symbol=Symbol("ETHUSDT"),
            base_currency=ETH,
            quote_currency=USDT,
            price_precision=2,
            size_precision=5,
            price_increment=Price(1e-02, precision=2),
            size_increment=Quantity(1e-05, precision=5),
            lot_size=None,
            max_quantity=Quantity(9000, precision=5),
            min_quantity=Quantity(1e-05, precision=5),
            max_notional=None,
            min_notional=Money(10.00, USDT),
            max_price=Price(1000000, precision=2),
            min_price=Price(0.01, precision=2),
            margin_init=Decimal("1.00"),
            margin_maint=Decimal("0.35"),
            maker_fee=Decimal("0.0001"),
            taker_fee=Decimal("0.0001"),
            ts_event=0,
            ts_init=0,
        )

    @staticmethod
    def ethusdt_perp_binance() -> CryptoPerpetual:
        """
        Return the Binance ETHUSDT-PERP instrument for backtesting.

        Returns
        -------
        CryptoPerpetual

        """
        return CryptoPerpetual(
            instrument_id=InstrumentId(
                symbol=Symbol("ETHUSDT-PERP"),
                venue=Venue("BINANCE"),
            ),
            native_symbol=Symbol("ETHUSDT"),
            base_currency=ETH,
            quote_currency=USDT,
            settlement_currency=USDT,
            is_inverse=False,
            price_precision=2,
            size_precision=3,
            price_increment=Price.from_str("0.01"),
            size_increment=Quantity.from_str("0.001"),
            max_quantity=Quantity.from_str("10000.000"),
            min_quantity=Quantity.from_str("0.001"),
            max_notional=None,
            min_notional=Money(10.00, USDT),
            max_price=Price.from_str("152588.43"),
            min_price=Price.from_str("29.91"),
            margin_init=Decimal("1.00"),
            margin_maint=Decimal("0.35"),
            maker_fee=Decimal("0.0002"),
            taker_fee=Decimal("0.0004"),
            ts_event=1646199312128000000,
            ts_init=1646199342953849862,
        )

    @staticmethod
    def btcusdt_future_binance(expiry: Optional[date] = None) -> CryptoFuture:
        """
        Return the Binance BTCUSDT instrument for backtesting.

        Parameters
        ----------
        expiry : date, optional
            The expiry date for the contract.

        Returns
        -------
        CryptoFuture

        """
        if expiry is None:
            expiry = date(2022, 3, 25)
        return CryptoFuture(
            instrument_id=InstrumentId(
                symbol=Symbol(f"BTCUSDT_{expiry.strftime('%y%m%d')}"),
                venue=Venue("BINANCE"),
            ),
            native_symbol=Symbol("BTCUSDT"),
            underlying=BTC,
            quote_currency=USDT,
            settlement_currency=USDT,
            expiry_date=expiry,
            price_precision=2,
            size_precision=6,
            price_increment=Price(1e-02, precision=2),
            size_increment=Quantity(1e-06, precision=6),
            max_quantity=Quantity(9000, precision=6),
            min_quantity=Quantity(1e-06, precision=6),
            max_notional=None,
            min_notional=Money(10.00000000, USDT),
            max_price=Price(1000000, precision=2),
            min_price=Price(0.01, precision=2),
            margin_init=Decimal(0),
            margin_maint=Decimal(0),
            maker_fee=Decimal("0.001"),
            taker_fee=Decimal("0.001"),
            ts_event=0,
            ts_init=0,
        )

    @staticmethod
    def xbtusd_bitmex() -> CryptoPerpetual:
        """
        Return the BitMEX XBT/USD perpetual contract for backtesting.

        Returns
        -------
        CryptoPerpetual

        """
        return CryptoPerpetual(
            instrument_id=InstrumentId(
                symbol=Symbol("BTC/USD"),
                venue=Venue("BITMEX"),
            ),
            native_symbol=Symbol("XBTUSD"),
            base_currency=BTC,
            quote_currency=USD,
            settlement_currency=BTC,
            is_inverse=True,
            price_precision=1,
            size_precision=0,
            price_increment=Price.from_str("0.5"),
            size_increment=Quantity.from_int(1),
            max_quantity=None,
            min_quantity=None,
            max_notional=Money(10_000_000.00, USD),
            min_notional=Money(1.00, USD),
            max_price=Price.from_str("1000000.0"),
            min_price=Price(0.5, precision=1),
            margin_init=Decimal("0.01"),
            margin_maint=Decimal("0.0035"),
            maker_fee=Decimal("-0.00025"),
            taker_fee=Decimal("0.00075"),
            ts_event=0,
            ts_init=0,
        )

    @staticmethod
    def ethusd_bitmex() -> CryptoPerpetual:
        """
        Return the BitMEX ETH/USD perpetual swap contract for backtesting.

        Returns
        -------
        CryptoPerpetual

        """
        return CryptoPerpetual(
            instrument_id=InstrumentId(
                symbol=Symbol("ETH/USD"),
                venue=Venue("BITMEX"),
            ),
            native_symbol=Symbol("ETHUSD"),
            base_currency=ETH,
            quote_currency=USD,
            settlement_currency=BTC,
            is_inverse=True,
            price_precision=2,
            size_precision=0,
            price_increment=Price.from_str("0.05"),
            size_increment=Quantity.from_int(1),
            max_quantity=Quantity.from_int(10000000),
            min_quantity=Quantity.from_int(1),
            max_notional=None,
            min_notional=None,
            max_price=Price.from_str("1000000.00"),
            min_price=Price.from_str("0.05"),
            margin_init=Decimal("0.02"),
            margin_maint=Decimal("0.007"),
            maker_fee=Decimal("-0.00025"),
            taker_fee=Decimal("0.00075"),
            ts_event=0,
            ts_init=0,
        )

    @staticmethod
    def default_fx_ccy(symbol: str, venue: Venue = None) -> CurrencyPair:
        """
        Return a default FX currency pair instrument from the given symbol and venue.

        Parameters
        ----------
        symbol : str
            The currency pair symbol.
        venue : Venue
            The currency pair venue.

        Returns
        -------
        CurrencyPair

        Raises
        ------
        ValueError
            If `symbol` length is not in range [6, 7].

        """
        if venue is None:
            venue = Venue("SIM")
        PyCondition.valid_string(symbol, "symbol")
        PyCondition.in_range_int(len(symbol), 6, 7, "len(symbol)")

        instrument_id = InstrumentId(
            symbol=Symbol(symbol),
            venue=venue,
        )

        base_currency = symbol[:3]
        quote_currency = symbol[-3:]

        # Check tick precision of quote currency
        if quote_currency == "JPY":
            price_precision = 3
        else:
            price_precision = 5

        return CurrencyPair(
            instrument_id=instrument_id,
            native_symbol=Symbol(symbol),
            base_currency=Currency.from_str(base_currency),
            quote_currency=Currency.from_str(quote_currency),
            price_precision=price_precision,
            size_precision=0,
            price_increment=Price(1 / 10**price_precision, price_precision),
            size_increment=Quantity.from_int(1),
            lot_size=Quantity.from_str("1000"),
            max_quantity=Quantity.from_str("1e7"),
            min_quantity=Quantity.from_str("1000"),
            max_price=None,
            min_price=None,
            max_notional=Money(50000000.00, USD),
            min_notional=Money(1000.00, USD),
            margin_init=Decimal("0.03"),
            margin_maint=Decimal("0.03"),
            maker_fee=Decimal("0.00002"),
            taker_fee=Decimal("0.00002"),
            ts_event=0,
            ts_init=0,
        )

    @staticmethod
    def aapl_equity():
        return Equity(
            instrument_id=InstrumentId(symbol=Symbol("AAPL"), venue=Venue("NASDAQ")),
            native_symbol=Symbol("AAPL"),
            currency=USD,
            price_precision=2,
            price_increment=Price.from_str("0.01"),
            multiplier=Quantity.from_int(1),
            lot_size=Quantity.from_int(1),
            isin="US0378331005",
            ts_event=0,
            ts_init=0,
        )

    @staticmethod
    def es_future():
        return Future(
            instrument_id=InstrumentId(symbol=Symbol("ESZ21"), venue=Venue("CME")),
            native_symbol=Symbol("ESZ21"),
            asset_class=AssetClass.INDEX,
            currency=USD,
            price_precision=2,
            price_increment=Price.from_str("0.01"),
            multiplier=Quantity.from_int(1),
            lot_size=Quantity.from_int(1),
            underlying="ES",
            expiry_date=date(2021, 12, 17),
            ts_event=0,
            ts_init=0,
        )

    @staticmethod
    def aapl_option():
        return Option(
            instrument_id=InstrumentId(symbol=Symbol("AAPL211217C00150000"), venue=Venue("OPRA")),
            native_symbol=Symbol("AAPL211217C00150000"),
            asset_class=AssetClass.EQUITY,
            currency=USD,
            price_precision=2,
            price_increment=Price.from_str("0.01"),
            multiplier=Quantity.from_int(100),
            lot_size=Quantity.from_int(1),
            underlying="AAPL",
            kind=OptionKind.CALL,
            expiry_date=date(2021, 12, 17),
            strike_price=Price.from_str("149.00"),
            ts_event=0,
            ts_init=0,
        )

    @staticmethod
    def betting_instrument(
        market_id: str = "1.179082386",
        selection_id: str = "50214",
        handicap: Optional[str] = None,
    ) -> BettingInstrument:
        return BettingInstrument(
            venue_name=BETFAIR_VENUE.value,
            betting_type="ODDS",
            competition_id="12282733",
            competition_name="NFL",
            event_country_code="GB",
            event_id="29678534",
            event_name="NFL",
            event_open_date=pd.Timestamp("2022-02-07 23:30:00+00:00"),
            event_type_id="6423",
            event_type_name="American Football",
            market_id=market_id,
            market_name="AFC Conference Winner",
            market_start_time=pd.Timestamp("2022-02-07 23:30:00+00:00"),
            market_type="SPECIAL",
            selection_handicap=handicap,
            selection_id=selection_id,
            selection_name="Kansas City Chiefs",
            currency="GBP",
            ts_event=0,
            ts_init=0,
        )

    @staticmethod
    def betting_instrument_handicap() -> BettingInstrument:
        return BettingInstrument.from_dict(
            {
                "venue_name": "BETFAIR",
                "event_type_id": "61420",
                "event_type_name": "Australian Rules",
                "competition_id": "11897406",
                "competition_name": "AFL",
                "event_id": "30777079",
                "event_name": "GWS v Richmond",
                "event_country_code": "AU",
                "event_open_date": "2021-08-13T09:50:00+00:00",
                "betting_type": "ASIAN_HANDICAP_DOUBLE_LINE",
                "market_id": "1.186249896",
                "market_name": "Handicap",
                "market_start_time": "2021-08-13T09:50:00+00:00",
                "market_type": "HANDICAP",
                "selection_id": "5304641",
                "selection_name": "GWS",
                "selection_handicap": "-5.5",
                "currency": "AUD",
                "ts_event": 0,
                "ts_init": 0,
            },
        )


class TestDataProvider:
    """
    Provides an API to load data from either the 'test/' directory or GitHub repo.

    Parameters
    ----------
    branch : str
        The NautilusTrader GitHub branch for the path.
    """

    def __init__(self, branch="develop"):
        self.fs: Optional[fsspec.AbstractFileSystem] = None
        self.root: Optional[str] = None
        self._determine_filesystem()
        self.branch = branch

    @staticmethod
    def _test_data_directory() -> Optional[str]:
        # Determine if the test data directory exists (i.e. this is a checkout of the source code).
        source_root = pathlib.Path(__file__).parent.parent.parent
        assert source_root.stem == "nautilus_trader"
        test_data_dir = source_root.parent.joinpath("tests", "test_data")
        if test_data_dir.exists():
            return str(test_data_dir)
        else:
            return None

    def _determine_filesystem(self):
        test_data_dir = TestDataProvider._test_data_directory()
        if test_data_dir:
            self.root = test_data_dir
            self.fs = fsspec.filesystem("file")
        else:
            print("Couldn't find test data directory, test data will be pulled from GitHub")
            self.root = "tests/test_kit/data"
            self.fs = fsspec.filesystem("github", org="nautechsystems", repo="nautilus_trader")

    def _make_uri(self, path: str):
        if isinstance(self.fs, LocalFileSystem):
            return f"file://{self.root}/{path}"
        elif isinstance(self.fs, GithubFileSystem):
            return f"github://{self.fs.org}:{self.fs.repo}@{self.branch}/{self.root}/{path}"

    def read(self, path: str):
        uri = self._make_uri(path=path)
        with fsspec.open(uri) as f:
            return f.read()

    def read_csv(self, path: str, **kwargs):
        uri = self._make_uri(path=path)
        with fsspec.open(uri) as f:
            return pd.read_csv(f, **kwargs)

    def read_csv_ticks(self, path: str):
        uri = self._make_uri(path=path)
        with fsspec.open(uri) as f:
            return CSVTickDataLoader.load(file_path=f)

    def read_csv_bars(self, path: str):
        uri = self._make_uri(path=path)
        with fsspec.open(uri) as f:
            return CSVBarDataLoader.load(file_path=f)

    def read_parquet_ticks(self, path: str, timestamp_column: str = "timestamp"):
        uri = self._make_uri(path=path)
        with fsspec.open(uri) as f:
            return ParquetTickDataLoader.load(file_path=f, timestamp_column=timestamp_column)

    def read_parquet_bars(self, path: str):
        uri = self._make_uri(path=path)
        with fsspec.open(uri) as f:
            return ParquetBarDataLoader.load(file_path=f)
