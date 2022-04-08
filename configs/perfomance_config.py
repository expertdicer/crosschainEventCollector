import os


class PerformanceConfig:
    CALCULATE_PERFORMANCE = os.environ.get("CALCULATE_PERFORMANCE") or True