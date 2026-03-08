from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import PermissionDenied


ROLE_HIERARCHY = {
    'superadmin': 9,
    'manager': 8,
    'accountant': 7,
    'warehouse': 6,
    'cashier': 5,
    'waiter': 4,
    'barista': 3,
    'tailor': 2,
}


class RoleRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    required_roles = []

    def test_func(self):
        user = self.request.user
        if not hasattr(user, 'staff_profile'):
            return False
        return user.staff_profile.role in self.required_roles or user.staff_profile.role == 'superadmin'

    def handle_no_permission(self):
        raise PermissionDenied
