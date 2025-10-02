from django.urls import path

from . import views

urlpatterns = [
    path('',views.agent_index_view,name="agent_index"),
    path('add_shop/',views.add_shop,name="add_shop"),
    path('super_admin/add_agent/',views.add_agent,name="add_agent"),
    path('get_shops_stat/',views.get_shop_stat,name="get_shops_stat"),
    path('super_admin/view_agent/<int:id>/get_shops_stat/',views.admin_get_shop_stat,name="admin_get_shops_stat"),
    path('super_admin/get_agent_stat/',views.get_agent_stat,name="get_agent_stat"),
    path('activate_deactivate/',views.activate_deactivate_view,name="activate_deactivate"),
    path('get_shop_info/',views.get_shop_info,name="get_shop_info"),
    path('add_balance/',views.add_balance,name="add_balance"),
    path('edit_shop/',views.edit_shop,name="edit_shop"),
    path('get_shops_stat_filter/',views.get_shop_stat_filter,name="get_shops_stat_filter"),
    path('super_admin/view_agent/<int:id>/get_shops_stat_filter/',views.admin_get_shop_stat_filter,name="admin_get_shops_stat_filter"),
    path('super_admin/activate_deactivate/',views.agent_activate_deactivate_view,name="agent_activate_deactivate"),
    path('super_admin/get_agent_info/',views.get_agent_info,name="get_agent_info"),
    path('super_admin/add_balance/',views.agent_add_balance,name="agent_add_balance"),
    path('super_admin/edit_agent/',views.edit_agent,name="edit_agent"),
    path('super_admin/',views.super_admin_view,name="super_admin"),
    path('super_admin/view_agent/<int:id>/',views.view_agent_view,name="view_agent"),
    path('create-agent-account/', views.create_agent_account, name='create_agent_account'),
    path('my-accounts/', views.list_my_accounts, name='list_my_accounts'),
    path('agent-accounts/', views.list_agent_accounts_for_shop, name='list_agent_accounts_for_shop'),
    path('shop-auto-deposit/', views.shop_auto_deposit, name='shop_auto_deposit'),
    path('transactions/', views.get_agent_dashboard_transactions, name='agent_transactions'),

]