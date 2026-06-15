def get_commodity_prices():
    """
    Returns current commodity prices and their market trends.
    Simulates Trading Economics API datasets.
    
    Returns:
        - commodities (dict)
        - commodity_risk (str): HIGH, MEDIUM, LOW
        - price_trend (str): UP, DOWN, STABLE
    """
    commodities = {
        "Palm Oil": {"price": 1150, "unit": "USD/MT", "trend": "UP"},
        "Sugar": {"price": 22.4, "unit": "USc/lb", "trend": "UP"},
        "Wheat": {"price": 680, "unit": "USc/bu", "trend": "STABLE"},
        "Milk Powder": {"price": 3450, "unit": "USD/MT", "trend": "UP"}
    }
    
    return {
        "commodities": commodities,
        "commodity_risk": "HIGH",
        "price_trend": "UP",
        "source": "Mock Trading Economics API"
    }
