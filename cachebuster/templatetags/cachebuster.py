__author__ = 'James Addison'

from django import template
from django.conf import settings
from django.contrib.staticfiles.storage import staticfiles_storage
from django.core.files.storage import default_storage

try:
    # finders won't exist if we're not using Django 1.3+
    from django.contrib.staticfiles import finders
except ImportError:
    finders = None


register = template.Library()


@register.tag(name="cachebustmedia")
def do_media(parser, token):
    return CacheBusterTag(token, True)


@register.tag(name="cachebuststatic")
def do_static(parser, token):
    return CacheBusterTag(token, False)


class CacheBusterTag(template.Node):
    def __init__(self, token, is_media):
        self.is_media = is_media

        try:
            tokens = token.split_contents()
        except ValueError:
            raise template.TemplateSyntaxError(
                "'%r' tag must have one or two arguments" %
                token.contents.split()[0])

        self.path = tokens[1]
        self.unique_string = getattr(
            settings, 'CACHEBUSTER_UNIQUE_STRING', 'no_cachebuster_set')

    def render(self, context):
        # self.path can be a template variable or a static string.
        try:
            path = template.Variable(self.path).resolve(context)
        except template.VariableDoesNotExist:
            path = self.path

        # The return value from the storage is urlencoded so we must remove the
        # query string.
        if '?' in path:
            path, query = path.split('?', 1)
            query = query + '&' + self.unique_string
        else:
            query = self.unique_string

        if self.is_media:
            return default_storage.url(path) + '?' + query
        else:
            return staticfiles_storage.url(path) + '?' + query
