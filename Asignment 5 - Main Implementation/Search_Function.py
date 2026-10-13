"""
Search Function Service — runs as a standalone process.
Communicates with the main program via JSON files:
  Request:  search_request.json
  Response: search_response.json
"""
import json
import os
import time


REQUEST_FILE  = "search_request.json"
RESPONSE_FILE = "search_response.json"


def search(query, data_file, search_fields=None, filters=None):
    """Search items in a JSON data file and return ranked results."""
    if len(query) < 2:
        return {'success': False, 'error': 'Query too short', 'results': [], 'count': 0}

    items = _load_data(data_file)
    if not items:
        return {'success': True, 'results': [], 'count': 0}

    if not search_fields:
        search_fields = _auto_detect_fields(items[0])

    query_lower = query.lower()
    results = []

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

    if filters:
        results = [r for r in results if all(r['item'].get(k) == v for k, v in filters.items())]

    results.sort(key=lambda r: r['score'], reverse=True)
    return {'success': True, 'results': [r['item'] for r in results], 'count': len(results)}


def _auto_detect_fields(sample):
    common = ['title', 'name', 'username', 'description', 'platform', 'category', 'status']
    return [k for k in sample.keys() if k in common or isinstance(sample[k], str)]


def _load_data(data_file):
    if os.path.exists(data_file):
        with open(data_file, 'r') as f:
            return json.load(f)
    return []


def handle_request(request):
    """Route an incoming request dict to the correct function and return a response dict."""
    action = request.get('action')

    if action == 'search_games':
        return search(
            request['query'],
            request.get('games_file', 'games.json'),
            ['title', 'platform', 'status'],
            request.get('filters')
        )

    return {'success': False, 'error': f"Unknown action: {action}"}


def run():
    """Main polling loop — watches for request file, processes it, writes response."""
    print("Search Function service running. Waiting for requests...")

    while True:
        if os.path.exists(REQUEST_FILE):
            try:
                with open(REQUEST_FILE, 'r') as f:
                    request = json.load(f)

                os.remove(REQUEST_FILE)
                response = handle_request(request)

                with open(RESPONSE_FILE, 'w') as f:
                    json.dump(response, f, indent=2)

                print(f"Search: handled '{request.get('action')}' -> {response.get('count', '?')} results")

            except Exception as e:
                error_response = {'success': False, 'error': str(e)}
                with open(RESPONSE_FILE, 'w') as f:
                    json.dump(error_response, f, indent=2)

        time.sleep(0.1)


if __name__ == "__main__":
    run()
