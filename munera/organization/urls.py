from django.urls import path
from .views import (
    JoinOrganizationView,
    LeaveOrganizationView,
    MyOrganizationsView,
    CreateOrganizationView,
    DeleteOrganizationView,
    OrganizationDetailView,
    OrganizationMemberRoleUpdateView,
)

urlpatterns = [
    path('', MyOrganizationsView.as_view(), name='my_organizations'),
    path('create/', CreateOrganizationView.as_view(), name='create_organization'),
    path('join/', JoinOrganizationView.as_view(), name='join_organization'),
    path('detail/<int:org_id>/', OrganizationDetailView.as_view(), name='organization_detail'),
    path('leave/<int:org_id>/', LeaveOrganizationView.as_view(), name='leave_organization'),
    path('delete/<int:org_id>/', DeleteOrganizationView.as_view(), name='delete_organization'),
    path('<int:org_id>/members/<int:user_id>/role/', OrganizationMemberRoleUpdateView.as_view(), name='update_member_role'),
]
