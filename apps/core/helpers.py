def set_list_filter(request):
    pass


def get_list_display_options(request, model):
    """ Returns display options from session, or defaults if not yet set """
    return (
        request.session.get(f"display_filter_{model}", "ALL"),
        request.session.get(f"display_order_{model}", "name"),
        request.session.get(f"display_page_size_{model}", 10),
    )


def get_page_context_options(app, model):
    return {
        "model": f"{model}",
        "url_add": f"apps.{app}:{model}_add",
        "url_list": f"apps.{app}:{model}_list",
        "url_detail": f"apps.{app}:{model}_detail",
        "url_edit": f"apps.{app}:{model}_edit",
        "title": f"{model.title()}",
    }
