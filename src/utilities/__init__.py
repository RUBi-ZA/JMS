from django.conf import settings


def deepgetattr(obj, attr):
    """Recurses through an attribute chain to get the ultimate value."""
    return reduce(getattr, attr.split('.'), obj)


def import_module(module_name):
    """dynamically import the resource manager module"""
    return __import__('jobs.JMS.resource_managers.%s' % module_name, fromlist=[module_name])


def import_class(module_name, class_name):
    """Import a class from a given module"""
    module = import_module(module_name)
    return getattr(module, module_name)