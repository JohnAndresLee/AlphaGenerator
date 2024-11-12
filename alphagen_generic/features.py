from alphagen.data.expression import Feature, Ref
from alphagen_qlib.stock_data import FeatureType


high = Feature(FeatureType.HIGH)
low = Feature(FeatureType.LOW)
volume = Feature(FeatureType.VOLUME)
open_ = Feature(FeatureType.OPEN)
close = Feature(FeatureType.CLOSE)
vwap = Feature(FeatureType.VWAP)
# quote_asset_volume = Feature(FeatureType.QUOTE_ASSET_VOLUME)
# number_of_trades = Feature(FeatureType.NUMBER_OF_TRADES)
# taker_buy_base_asset_volume = Feature(FeatureType.TAKER_BUY_BASE_ASSET_VOLUME)
# taker_buy_quote_asset_volume = Feature(FeatureType.TAKER_BUY_QUOTE_ASSET_VOLUME)

target = Ref(close, -20) / close - 1