from django.shortcuts import get_object_or_404
from django.core.exceptions import PermissionDenied

from jobs.models import Category


def GetCategory(CategoryID):
    return get_object_or_404(Category, pk=CategoryID)


def GetCategories():
    return Category.objects.all().order_by('CategoryName')


def AddCategory(user, CategoryName):
    return Category.objects.create(CategoryName=CategoryName)


def DeleteCategory(user, CategoryID):
    category = GetCategory(CategoryID)
    if len(category.Tools.all()) == 0:
        category.delete()
    else:
        raise PermissionDenied


def UpdateCategory(user, CategoryID, CategoryName):
    category = GetCategory(CategoryID)
    category.CategoryName = CategoryName
    category.save()
    return category