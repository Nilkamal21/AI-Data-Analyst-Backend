import math
import numpy as np

def clean_for_json(data):
    if isinstance(data, dict):
        return {k: clean_for_json(v) for k, v in data.items()}
    
    elif isinstance(data, list):
        return [clean_for_json(v) for v in data]
    
    elif isinstance(data, float):
        if math.isnan(data) or math.isinf(data):
            return None
        return data
    
    elif isinstance(data, np.generic):
        return data.item()
    
    else:
        return data