from sanic import Sanic, Request, response
from urllib.parse import urlencode

def error_redirect(request: Request, msg: str, route: str = "/auth/login"):
    """
    A function to handle errors by redirecting the user either to a 
    specified route or to the current route with an error message as a query parameter.

    :param request: Sanic's request object to get the current path
    :param msg: Error message to be shown.
    :param route: Optional route to redirect to. Defaults to None, which uses the current route.
    :return: A response that either redirects to the specified route or to the current route with error message.
    """
    # If no redirect route is specified, return the user to the current route with error message
    route = f"{route}?{urlencode({'error': msg})}"
    
    # Redirect to the specified route with the error message
    return response.redirect(route)