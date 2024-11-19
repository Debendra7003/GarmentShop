import json
from decimal import Decimal
from rest_framework.renderers import JSONRenderer

class UserRenderer(JSONRenderer):
    def render(self, data, accepted_media_type=None, renderer_context=None):
        # Convert any Decimal values to float before rendering
        if isinstance(data, dict):
            data = self.convert_decimals(data)
        response = json.dumps(data)
        return response.encode('utf-8')

    def convert_decimals(self, obj):
        if isinstance(obj, dict):
            return {k: self.convert_decimals(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self.convert_decimals(i) for i in obj]
        elif isinstance(obj, Decimal):
            return float(obj)
        return obj
