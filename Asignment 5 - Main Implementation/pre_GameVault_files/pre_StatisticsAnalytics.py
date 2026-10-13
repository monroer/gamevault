"""
Statistics/Analytics Service
Calculates summary stats for any list of JSON objects stored in a file.
 
Usage example (GameVault):
    get_stats('games.json', numeric_fields=['playtime', 'rating'], group_by='status')
 
Usage example (recipe app):
    get_stats('recipes.json', numeric_fields=['cook_time'], group_by='category')
"""
import json
import os
 
 
def get_stats(data_file, numeric_fields=None, group_by=None):
    """
    Returns summary stats for any JSON data file.
    - numeric_fields: list of keys to calculate totals/averages for (like ['playtime' or 'rating'])
    - group_by: a key to count items by category ('status', 'genre', 'category')
    """
    items = _load(data_file)
    if not items:
        return {'success': False, 'error': 'No data found in file.'}
 
    result = {'total_items': len(items)}
 
    if group_by:
        counts = {}
        for item in items:
            key = str(item.get(group_by, 'Unknown'))
            counts[key] = counts.get(key, 0) + 1
        result[f'{group_by}_breakdown'] = counts
 
    if numeric_fields:
        result['numeric_summaries'] = {}
        for field in numeric_fields:
            values = []
            for item in items:
                try:
                    values.append(float(item[field]))
                except (ValueError, TypeError, KeyError):
                    pass
            if values:
                result['numeric_summaries'][field] = {
                    'total': round(sum(values), 2),
                    'average': round(sum(values) / len(values), 2),
                    'min': min(values),
                    'max': max(values),
                }
 
    return {'success': True, 'stats': result}
 
 
def get_top_items(data_file, sort_field, limit=5, reverse=True):
    """
    Returns the top N items sorted by any numeric field.
    - sort_field: the key to sort by ('playtime', 'price', 'rating')
    - reverse=True returns highest first; False returns lowest first
    """
    items = _load(data_file)
    if not items:
        return {'success': False, 'error': 'No data found in file.'}
    sortable = [i for i in items if _is_number(i.get(sort_field))]
    if not sortable:
        return {'success': False, 'error': f"No numeric values found for field '{sort_field}'."}
    sorted_items = sorted(sortable, key=lambda i: float(i[sort_field]), reverse=reverse)
    return {'success': True, 'results': sorted_items[:limit]}
 
 
def _load(data_file):
    if os.path.exists(data_file):
        with open(data_file, 'r') as f:
            return json.load(f)
    return []
 
def _is_number(value):
    try:
        float(value)
        return True
    except (ValueError, TypeError):
        return False
 
