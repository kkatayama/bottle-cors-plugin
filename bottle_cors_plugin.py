from bottle import route, response, Bottle, request, HTTPError


class CorsPluginObject():

    name = 'cors'
    api = 2

    def __init__(self, origins="*"):
        """ Constructor function

            param: bottle
            ptype: Bottle class
            param: origins
            ptype: string or array
        """
        bottle = Bottle()
        bottle.cors = True
        self.origins = origins
        self.bottle = bottle
        self.fqdn = ""
        self._options_route()

    def apply(self, fn, context):
        def _enable_cors(*args, **kwargs):
            self.cors_headers()
            if request.method != 'OPTIONS':
                return fn(*args, **kwargs)

        return _enable_cors

    def _options_route(self):
        """
        Adds the OPTIONS route to all endpoints.
        """
        route('/', method='OPTIONS', callback=self.options_function)
        route('/<filepath:path>', method='OPTIONS', callback=self.options_function)

    def options_function(self):
        pass

    def cors_headers(self):
        response.headers['Access-Control-Allow-Origin'] = self._get_origin()
        response.add_header('Access-Control-Allow-Methods',
                             'GET, POST, PUT, PATCH, OPTIONS, DELETE, HEAD')
        response.add_header('Access-Control-Allow-Headers',
                             'Origin, Accept, Content-Type, X-Requested-With, X-CSRF-Token, Authorization')
        response.add_header('Access-Control-Allow-Credentials', 'true')

    def _get_origin(self):
        """
        Returns the origin if found on the allowed origins list.
        """
        client_origin = request.headers.get('Origin', None)
        if '*' in self.origins: return '*'
        if not client_origin:
            return self.origins[0]

        # Add all origins ever seen
        if client_origin not in self.origins:
            self.origins.append(client_origin)
            self.fqdn = client_origin

        for origin in self.origins:
            if origin == client_origin:
                self.fqdn = origin
                return origin
        return self.origins[0]

    def abort(self, code=500, text='Unknown Error.'):
        """
        Aborts execution and causes a HTTP error. 
        """
        self.cors_headers()
        headers = response.headers.dict
        headerlist = response.headerlist
        for name, value in headerlist:
            headers[name] = '%s' % (value.strip())
        raise HTTPError(code, text, headers=headers)


cors_plugin_object = CorsPluginObject()

def cors_plugin(origins="*"):
    if not isinstance(origins, list):
        origins = [origins]
    cors_plugin_object.origins = origins
    return cors_plugin_object

abort = cors_plugin_object.abort
cors_headers = cors_plugin_object.cors_headers

