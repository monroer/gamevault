"""Search Function Service"""
import json
import os

def search(query, data_file, search_fields=None, filters=None):
    """Search function for different data types"""
    if len(query) < 2:
        return {'success': False, 'error': 'Query too short', 'results': [], 'count': 0}
    
    items = load_data(data_file)
    if not items:
        return {'success': True, 'results': [], 'count': 0}
    
    # auto detect fields if not specified
    if not search_fields:
        search_fields = auto_detect_fields(items[0])

    # Search and score
    results = []
    query_lower = query.lower()

    for item in items:
        score = 0
        for field in search_fields:
            if field in item:
                value = str(item[field]).lower()
                if value == query_lower:
                    score += 10
                elif value.startswith(query_lower):
                    score += 5
                elif query_lower in value:
                    score += 3

        if score > 0:
            results.append({'item': item, 'score': score})

    # Apply filters
    if filters:
        results = [r for r in results if all(r['item'].get(k) == v for k, v in filters.items())]

    # Sort by score
    results.sort(key=lambda r: r['score'], reverse=True)

    return {'success': True, 'results': [r['item'] for r in results], 'count': len(results)}

def auto_detect_fields(sample):
    """Find searchable text fields"""
    common = ['title', 'name', 'username', 'description', 'platform', 'category', 'status']
    return [k for k in sample.keys() if k in common or isinstance(sample[k], str)]

def load_data(data_file):
    """Load JSON data"""
    if os.path.exists(data_file):
        with open(data_file, 'r') as f:
            return json.load(f)
    return []


# Convenience functions
def search_games(query, games_file='games.json', filters=None):
    return search(query, games_file, ['title', 'platform', 'status'], filters)

def search_users(query, users_file='users.json'):
    return search(query, users_file, ['username', 'email'])

def search_products(query, products_file='products.json', filters=None):
    return search(query, products_file, ['name', 'description', 'category'], filters)