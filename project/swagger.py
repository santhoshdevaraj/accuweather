from rest_framework_swagger.renderers import OpenAPIRenderer, SwaggerUIRenderer
from rest_framework.decorators import api_view, renderer_classes
from rest_framework import response, schemas


@api_view()
@renderer_classes([SwaggerUIRenderer, OpenAPIRenderer])
def schema_view(request) -> response.Response:
    """
    Return configuration details for DRF Swagger.
    """
    generator = schemas.SchemaGenerator(title='WeatherDetail API')
    return response.Response(generator.get_schema())