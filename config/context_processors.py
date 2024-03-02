from config import settings
from utils import Category


def context_processor(req):
    return {
        "RETURN_RATE": settings.RETURN_RATE,
        "RETURN_PERCENT": settings.RETURN_PERCENT,
        "POINT_PER": settings.POINT_PER,
        "CANCELLATION_FEE": settings.CANCELLATION_FEE,
        "MONEY_UNIT": settings.MONEY_UNIT,
        "CATEGORIES": Category.all(),
        "EXPRESS_PRICE": settings.EXPRESS_PRICE,
        "PRIDE_MONTHLY": settings.PRIDE_MONTHLY,
        "PRIDE_YEARLY": settings.PRIDE_YEARLY,
    }
