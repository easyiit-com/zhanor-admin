<!-- index.jinja2 -->
{% extends "admin/layout/default.jinja2" %}
{% block javascript %}
<script>
    $(document).ready(function () {
        "user strict";
        $(".select-all").click(function () {
            var isChecked = $(this).prop("checked");
            $(".id-checkbox").prop("checked", isChecked);
        });
        $('.delete-selected').click(function () {
            var selectedIds = [];
            $('.id-checkbox:checked').each(function () {
                selectedIds.push($(this).val());
            });
            if (selectedIds.length > 0) {
                if (confirm(_('Are you sure you want to delete it?'))) {
                    $.ajax({
                        type: "DELETE",
                        url: "/admin/%%route%%/delete",
                        contentType: 'application/json',
                        data: JSON.stringify({ ids: selectedIds }),
                        dataType: 'json',
                        success: function (response) {
                            for (var i = 0; i < selectedIds.length; i++) {
                                const thisElement = document.getElementById('%%model_name%%-' + selectedIds[i]);
                                if (thisElement) {
                                    thisElement.remove();
                                }
                            }
                            toastr.success(_('Delete Successfully'))
                        },
                        error: function (xhr, status, error) {
                            toastr.error(_('Delete Faile'), xhr.responseText);
                        }
                    });
                }
            } else {
                toastr.warning(_('Please first select the items you want to delete'));
            }
        });
        $('.btn-delete').click(function (event) {
            event.preventDefault();
            var $this = $(this);
            var %%model_class_name%%Id = $this.data('id');
            if (confirm(_('Are you sure you want to delete it?'))) {
                const selectedIds = [%%model_class_name%%Id];
                $("#app-loading-indicator").removeClass("opacity-0");
                $.ajax({
                    type: "DELETE",
                    url: "/admin/%%route%%/delete",
                    contentType: 'application/json',
                    data: JSON.stringify({ ids: selectedIds }),
                    processData: false,
                    success: function (data) {
                        const thisElement = $('#%%model_name%%-' + %%model_class_name%%Id);
                        if (thisElement.length) {
                            thisElement.remove();
                        }
                        toastr.success(_("Delete Successfully"));
                    },
                    error: function (xhr, status, error) {
                        let msg = xhr.responseJSON.msg;
                        toastr.error(_(msg));
                    },
                    complete: function (xhr, textStatus) {
                        $("#app-loading-indicator").addClass("opacity-0");
                    },
                });
            }
            return false;
        })
    });
</script>
{% endblock javascript %}
{% block content %}
<div class="page-body pt-6888">
    <div class="container-fluid px-4">
        <div class="mb-2">
            <a href="/admin/%%route%%/add" class="btn btn-success">
                <i class="ti ti-plus"></i>
                {{_('Add')}}
            </a>
            <a href="javascript:void(0)" class="btn delete-selected btn-warning">
                <i class="ti ti-trash"></i>
                {{_('Batch Deletion')}}
            </a>
        </div>
        <div class="card">
            <div id="table-default" class="card-table table-responsive">
                <table class="table action-table">
                    <thead>
                        <tr>
                            %%table_ths%%
                            <th class="!text-end">{{_('Actions')}}</th>
                        </tr>
                    </thead>
                    <tbody class="table-tbody align-middle text-heading">
                        <!-- TODO -->
                        {% for value in %%model_name%%_list %}
                        <tr id="%%model_name%%-{{ value.id }}">
                            %%table_tds%%
                            <td class="!text-end whitespace-nowrap">
                                <a href="javascript:;"
                                    class="btn w-[36px] h-[36px] p-0 border hover:bg-[var(--tblr-primary)] hover:text-white"
                                    data-bs-toggle="modal" data-bs-target="#modal-{{ value.id }}" title="View Details">
                                    <i class="ti ti-eye"></i>
                                </a>
                                <a href="/admin/%%route%%/edit/{{value.id}}"
                                    class="btn w-[36px] h-[36px] p-0 border hover:bg-[var(--tblr-primary)] hover:text-white"
                                    title="Edit">
                                    <i class="ti ti-edit"></i>
                                </a>
                                <a href="javascript:void(0)"
                                    class="btn btn-delete w-[36px] h-[36px] p-0 border hover:bg-red-500 hover:text-white"
                                    title="Delete" data-id="{{value.id}}">
                                    <i class="ti ti-x"></i>
                                </a>
                            </td>
                        </tr>
                        {% endfor %}
                    </tbody>
                    <tfoot>

                    </tfoot>
                </table>

            </div>
            <div
                class="flex items-center border-solid border-t border-r-0 border-b-0 border-l-0 border-[--tblr-border-color] px-[--tblr-card-cap-padding-x] py-[--tblr-card-cap-padding-y] [&_.rounded-md]:rounded-full">
                <div class="m-0 ms-auto p-0">
                    <ul class="pagination ">
                        {% if current_page > 1 %}
                        <li class="page-item">
                            <a class="page-link" href="?page={{ current_page - 1 }}" tabindex="-1" aria-disabled="true">
                                <i class="ti ti-arrow-left"></i>
                                {{_('Prev')}}
                            </a>
                        </li>
                        {% endif %}

                        {% for i in range(1, total_pages + 1) %}
                        {% if i == current_page %}
                        <li class="page-item active"><a class="page-link" href="#">{{ i }}</a></li>

                        {% else %}
                        <li class="page-item"><a class="page-link" href="?page={{ i }}">{{ i }}</a></li>
                        {% endif %}
                        {% endfor %}

                        {% if current_page < total_pages %} <li class="page-item">
                            <a class="page-link" href="?page={{ current_page + 1 }}">
                                {{_('next')}}
                                <i class="ti ti-arrow-right"></i>
                            </a>
                            </li>
                            {% endif %}
                    </ul>
                </div>
            </div>
        </div>
    </div>
</div>
{% for value in %%model_name%%_list %}
<div class="modal modal-blur fade" id="modal-{{ value.id }}" tabindex="-1" role="dialog" aria-hidden="true">
    <div class="modal-dialog modal-dialog-centered" role="document">
        <div class="modal-content">
            <div class="modal-header">
                <h5 class="modal-title">{{_('Details')}} ID:{{value.id}}</h5>
                <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
            </div>
            <div class="modal-body">
                %%table_details%%
            </div>
            <div class="modal-footer">
                <button type="button" class="btn btn-primary" data-bs-dismiss="modal">{{_('Close')}}</button>
            </div>
        </div>
    </div>
</div>
{% endfor %}
{% endblock content %}