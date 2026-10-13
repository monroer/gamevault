"""
Statistics / Analytics Service — runs as a standalone process.
Communicates with the main program via JSON files:
  Request:  stats_request.json
  Response: stats_response.json
"""
import json
import os
import time


REQUEST_FILE  = "stats_request.json"
RESPONSE_FILE = "stats_response.json"


def get_stats(data_file, numeric_fields=None, group_by=None):
    """Returns summary stats for any JSON data file."""
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
                    'total':   round(sum(values), 2),
                    'average': round(sum(values) / len(values), 2),
                    'min':     min(values),
                    'max':     max(values),
                }

    return {'success': True, 'stats': result}


def get_top_items(data_file, sort_field, limit=5, reverse=True):
    """Returns the top N items sorted by any numeric field."""
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


def handle_request(request):
    """Route an incoming request dict to the correct function and return a response dict."""
    action = request.get('action')

    if action == 'get_stats':
        return get_stats(
            request['data_file'],
            numeric_fields=request.get('numeric_fields'),
            group_by=request.get('group_by')
        )

    if action == 'get_top_items':
        return get_top_items(
            request['data_file'],
            sort_field=request['sort_field'],
            limit=request.get('limit', 5),
            reverse=request.get('reverse', True)
        )

    return {'success': False, 'error': f"Unknown action: {action}"}


def run():
    """Main polling loop — watches for request file, processes it, writes response."""
    print("Statistics Analytics service running. Waiting for requests...")

    while True:
        if os.path.exists(REQUEST_FILE):
            try:
                with open(REQUEST_FILE, 'r') as f:
                    request = json.load(f)

                os.remove(REQUEST_FILE)
                response = handle_request(request)

                with open(RESPONSE_FILE, 'w') as f:
                    json.dump(response, f, indent=2)

                print(f"Statistics: handled '{request.get('action')}'")

            except Exception as e:
                error_response = {'success': False, 'error': str(e)}
                with open(RESPONSE_FILE, 'w') as f:
                    json.dump(error_response, f, indent=2)

        time.sleep(0.1)


if __name__ == "__main__":
    run()
