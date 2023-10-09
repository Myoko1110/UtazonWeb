from config import settings
from util import Category


def context_processor(req):
    return {
        "RETURN_RATE": settings.RETURN_RATE,
        "RETURN_PERCENT": settings.RETURN_PERCENT,
        "POINT_PER": settings.POINT_PER,
        "CANCELLATION_FEE": settings.CANCELLATION_FEE,
        "MONEY_UNIT": settings.MONEY_UNIT,
        "CATEGORIES": Category.all(),
    }
