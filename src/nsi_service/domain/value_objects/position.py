from enum import Enum


class Position(str, Enum):
    """Позиция на поле"""

    GK = "goalkeeper"
    CB = "center_back"
    LB = "left_back"
    RB = "right_back"
    CDM = "defensive_midfielder"
    CM = "central_midfielder"
    CAM = "attacking_midfielder"
    LW = "left_winger"
    RW = "right_winger"
    ST = "striker"
    UNKNOWN = "unknown"

    @classmethod
    def get_main_category(cls, position: "Position") -> str:
        """Получить основную категорию позиции"""
        categories = {
            "GK": [cls.GK],
            "DEF": [cls.CB, cls.LB, cls.RB],
            "MID": [cls.CDM, cls.CM, cls.CAM],
            "FWD": [cls.LW, cls.RW, cls.ST],
        }

        for category, positions in categories.items():
            if position in positions:
                return category
        return "UNKNOWN"
