function refreshTags(input) {
    if(input.parent().attr('class').includes("bootstrap-tagsinput")) {
        if(input.parent().attr('class').includes("sr-only")) {
            input.parent().remove();
        } else {
            input.parent().tagsinput('refresh');
        }
        return true;
    }
    return false;
}

$(function() {
    $("div[data-toggle=fieldset]").each(function() {
        var $this = $(this);

        //Add new entry
        $this.find("button[data-toggle=fieldset-add-row]").click(function() {
            var target = $($(this).data("target"));
            var oldrow = target.find("[data-toggle=fieldset-entry]:first");
            var row = oldrow.clone(true, true);
            var elem_id = row.find(":input")[0].id;
            var elem_num = parseInt(elem_id.replace(/.*-(\d{1,4})-.*/m, '$1')) + 1;
            row.attr('data-id', elem_num);
            row.find(":input").each(function() {
                if(!refreshTags($(this)))
                {
                   var id = $(this).attr('id').replace('-' + (elem_num - 1) + '-', '-' + (elem_num) + '-');
                    $(this).attr('name', id).attr('id', id).val('').removeAttr("checked");
                }

            });
            //row.find('button').css('display', 'block');
            row.css('display', 'none').fadeIn();
            oldrow.before(row);
            oldrow.find(":input").each(function() {
                if($(this).parent().attr('class').includes("bootstrap-tagsinput sr-only")) {
                    $(this).parent().remove();
                }
            });
        });

        //Remove row
        $this.find("button[data-toggle=fieldset-remove-row]").click(function() {
            if($this.find("[data-toggle=fieldset-entry]").length > 1) {
                var thisRow = $(this).closest("[data-toggle=fieldset-entry]");
                if(thisRow.attr('data-id') == 0) {
                    thisRow.find(":input").each(function() {
                        if(!refreshTags($(this))) {
                            $(this).val('');
                        }
                    });
                }
                else {
                    thisRow.fadeOut(function(){
                    thisRow.remove();
                    }
                )}
            }
        });
    });
});