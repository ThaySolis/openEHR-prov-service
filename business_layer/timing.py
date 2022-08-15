from data_layer.time_measurement import Timed, NotTimed
from app_settings import USAGE_STATISTICS_MAX_SAMPLES, INCLUDE_USAGE_STATISTICS

GET_PROVENANCE_MEASUREMENT = "get_provenance"

ALL_MEASUREMENTS = [GET_PROVENANCE_MEASUREMENT]

if INCLUDE_USAGE_STATISTICS:
    timed = Timed(USAGE_STATISTICS_MAX_SAMPLES)
else:
    timed = NotTimed()
