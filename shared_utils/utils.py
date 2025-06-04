import datetime
import json

def format_datetime(dt_object):
    """Formats a datetime object into a standard string format."""
    if dt_object:
        return dt_object.strftime("%Y-%m-%d %H:%M:%S")
    return None

def parse_datetime(dt_string):
    """Parses a datetime string into a datetime object."""
    if dt_string:
        try:
            return datetime.datetime.strptime(dt_string, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            return None
    return None

def generate_response(data=None, message="", success=True, status_code=200):
    """Generates a consistent JSON response structure."""
    response = {
        "success": success,
        "message": message,
        "data": data,
    }
    # For Flask, you might return jsonify(response), status_code
    return response # Or json.dumps(response) if not using Flask's jsonify

class EnhancedJSONEncoder(json.JSONEncoder):
    """
    A JSON encoder that handles datetime objects and other custom types.
    """
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return obj.isoformat()
        # Add other custom types here if needed
        return super().default(obj)

def serialize_to_json(data):
    """Serializes Python objects (including datetime) to a JSON string."""
    return json.dumps(data, cls=EnhancedJSONEncoder)

print("Shared utilities loaded.")
