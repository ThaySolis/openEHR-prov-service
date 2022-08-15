from data_layer.time_measurement import TimedGroup
from business_layer.timing import timed, ALL_MEASUREMENTS

def get_usage_statistics():
    usage_statistics = {}

    for measurement_name in ALL_MEASUREMENTS:
        group = timed.get_group(measurement_name)

        usage_statistics[measurement_name] = extract_statistics(group)

    return usage_statistics

def clear_usage_statistics():
    timed.clear_all()

def extract_statistics(group : TimedGroup) -> dict:
    return {
        "samples": group.get_samples()
    }
