from .data_provider import get_meta

def hints(user_guess, answer):
    user_meta, answer_meta = get_meta(user_guess), get_meta(answer)

    compare_price = user_meta["Price"] - answer_meta["Price"]
    compare_day_high = user_meta["Day High"] - answer_meta["Day High"]
    compare_day_low = user_meta["Day Low"] - answer_meta["Day Low"]
    compare_average_volume = user_meta["Average Volume"] - answer_meta["Average Volume"]
    compare_market_cap = user_meta["Market Cap"] - answer_meta["Market Cap"]

    return {
        "price": compare_price,
        "day_high": compare_day_high,
        "day_low": compare_day_low,
        "avg_volume": compare_average_volume,
        "market_cap": compare_market_cap,
    }