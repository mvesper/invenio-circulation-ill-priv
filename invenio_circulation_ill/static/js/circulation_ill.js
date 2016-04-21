/*
 * This file is part of Invenio.
 * Copyright (C) 2015 CERN.
 *
 * Invenio is free software; you can redistribute it and/or
 * modify it under the terms of the GNU General Public License as
 * published by the Free Software Foundation; either version 2 of the
 * License, or (at your option) any later version.
 *
 * Invenio is distributed in the hope that it will be useful, but
 * WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
 * General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with Invenio; if not, write to the Free Software Foundation, Inc.,
 * 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.
 */

define(
    [
        'jquery',
        'node_modules/bootstrap-datepicker/js/bootstrap-datepicker',
    ],
function($, _bdp) {
    $('#entity_detail').ready(function() {
        if ($('#entity_detail').length == 0) {
            return;
        }
        var editor = $('#entity_detail');
        var data = JSON.parse(editor.attr('data-editor_data'));
        var schema = JSON.parse(editor.attr('data-editor_schema'));

        json_editor = new JSONEditor($('#entity_detail')[0], 
                {
                    schema: schema,
                    theme: 'bootstrap3',
                    no_additional_properties: true,
                });
        json_editor.setValue(data);
    });

    $('#ill_request_submit').on('click', function(){
        // Get record values
        var rec = {};
        var active_form = $('.ill_document').not('.hidden');
        active_form.find('.form-control').each(function(index, element) {
            rec[$(element).data('value_name')] = element.value;
        });

        // Get user values
        var user = {};
        $('#user_form').find('.form-control').each(function(index, element) {
            user[$(element).data('value_name')] = element.value;
        });

        var record_id = $(active_form).data('record_id');
        var type = $(active_form).data('type');
        var start_date = $('#ill_date_from').val();
        var end_date = $('#ill_date_to').val();
        var comments = $('#request_comments').val();
        var delivery = $('#circulation_option_delivery').val();

        if ($(this).data('action') == 'request'){
            var url = '/circulation/api/ill/request_ill/';
        } else {
            var url = '/circulation/api/ill/register_ill/';
        }

        var data = {record: rec, user: user, type: type, record_id: record_id,
                    start_date: start_date, end_date: end_date,
                    comments: comments, delivery: delivery};

        function success() {
            $(document).scrollTop(0);
            window.location.reload();
        }

        $.ajax({
            type: "POST",
            url: url,
            data: JSON.stringify(JSON.stringify(data)),
            success: success,
            contentType: 'application/json',
        });
    });

    $('#ill_date_from').datepicker({ format: 'yyyy-mm-dd' });
    $('#ill_date_to').datepicker({ format: 'yyyy-mm-dd' });

    $('.ill_request_type').on('click', function(event) {
        var list_item = event.target.parentElement;
        if (!$(list_item).hasClass('active')) {
            $(list_item.parentElement).find('.active').removeClass('active');
            $(list_item).addClass('active');

            $('#ill_documents').children().each(function(i, doc) {
                if ($(doc).hasClass('hidden')) {
                    $(doc).removeClass('hidden');
                } else {
                    $(doc).addClass('hidden');
                }
            });
        }
    });
});
