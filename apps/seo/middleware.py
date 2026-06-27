from django.shortcuts import redirect
from .models import RedirectRule


class RedirectRuleMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        rule = RedirectRule.objects.filter(old_path=request.path, is_active=True).first()
        if rule:
            return redirect(rule.new_path, permanent=rule.permanent)
        return self.get_response(request)
