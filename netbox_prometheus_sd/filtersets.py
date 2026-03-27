# Filtersets have been renamed, we support both
# https://github.com/netbox-community/netbox/commit/1024782b9e0abb48f6da65f8248741227d53dbed#diff-d9224204dab475bbe888868c02235b8ef10f07c9201c45c90804d395dc161c40
from django.db.models import Q
from django_filters import CharFilter
from django.utils.translation import gettext as _

from utilities.filters import (
    MultiValueCharFilter,
    MultiValueNumberFilter,
    NumericArrayFilter,
)

try:
    from ipam.filtersets import ServiceFilterSet as NetboxServiceFilterSet
    from dcim.filtersets import DeviceFilterSet as NetboxDeviceFilterSet
    from virtualization.filtersets import VirtualMachineFilterSet as NetboxVirtualMachineFilterSet
except ImportError:
    from ipam.filters import ServiceFilterSet as NetboxServiceFilterSet
    from dcim.filters import DeviceFilterSet as NetboxDeviceFilterSet
    from virtualization.filters import VirtualMachineFilterSet as NetboxVirtualMachineFilterSet


class ServiceFilterSet(NetboxServiceFilterSet):
    """Filter set to support tenancy over the device/VM foreign key.

    Tenancy in Netbox is very incosistent and the relationship on its own is defined across many different models. This
    means that supporting all layers is nearly impossible without a stronger upstream support. For this reason only the
    "first level" tenancy is supported by this filter set.
    """

    tenant_id = MultiValueNumberFilter(
        method="filter_by_tenant_id",
        label=_("Tenant (ID)"),
    )

    tenant = MultiValueCharFilter(
        method="filter_by_tenant_slug",
        label=_("Tenant (slug)"),
    )

    # fix to make the test_missing_filters pass
    # see: https://github.com/netbox-community/netbox/blob/master/netbox/utilities/testing/filtersets.py#L98
    ports = NumericArrayFilter(field_name="ports", lookup_expr="contains")

    def filter_by_cluster_tenant_id(self, queryset, name, value):
        return queryset.filter(
            Q(device__cluster__tenant_id__in=value)
            | Q(virtual_machine__cluster__tenant_id__in=value)
        )

    def filter_by_cluster_tenant_slug(self, queryset, name, value):
        return queryset.filter(
            Q(device__cluster__tenant__slug__in=value)
            | Q(virtual_machine__cluster__tenant__slug__in=value)
        )

    def filter_by_tenant_id(self, queryset, name, value):
        return queryset.filter(
            Q(device__tenant_id__in=value) | Q(virtual_machine__tenant_id__in=value)
        )

    def filter_by_tenant_slug(self, queryset, name, value):
        return queryset.filter(
            Q(device__tenant__slug__in=value)
            | Q(virtual_machine__tenant__slug__in=value)
        )


class DeviceFilterSet(NetboxDeviceFilterSet):
    """Filter set to support site status and site tags filtering.
    
    Extends the base DeviceFilterSet to add filtering capabilities for:
    - site__status: Filter devices by their site's status
    - site__tag: Filter devices by their site's tags
    """

    site_status = CharFilter(
        method="filter_by_site_status",
        label=_("Site Status"),
    )

    site_tag = CharFilter(
        method="filter_by_site_tag",
        label=_("Site Tag"),
    )

    def filter_by_site_status(self, queryset, name, value):
        """Filter devices by site status."""
        return queryset.filter(site__status=value)

    def filter_by_site_tag(self, queryset, name, value):
        """Filter devices by site tags."""
        return queryset.filter(site__tags__name=value)

class VirtualMachineFilterSet(NetboxVirtualMachineFilterSet):
    """Filter set to support site status and site tags filtering.
    
    Extends the base VirtualMachineFilterSet to add filtering capabilities for:
    - site__status: Filter virtual machines by their site's status
    - site__tag: Filter virtual machines by their site's tags
    """

    site_status = CharFilter(
        method="filter_by_site_status",
        label=_("Site Status"),
    )

    site_tag = CharFilter(
        method="filter_by_site_tag",
        label=_("Site Tag"),
    )

    def filter_by_site_status(self, queryset, name, value):
        """Filter devices by site status."""
        return queryset.filter(site__status=value)

    def filter_by_site_tag(self, queryset, name, value):
        """Filter devices by site tags."""
        return queryset.filter(site__tags__name=value)
