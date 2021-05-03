function deleteItem(button) {

    var url = null; 
    var deleteId = $(button).attr('name');
    if ( $(button).attr('id') == 'reportedPosts'){
        url = "delete-post/" + deleteId;
    } else if ( $(button).attr('id') == 'reportedUsers' ) {
        url = "delete-user/" + deleteId;
    }

    $.ajax( url , {
        type: 'PUT',
        success: function (data, status, xhr) {
            $(button).prop("disabled",true);

            console.log('status: ' + status + ', data: ' + data);
        },
        error: function (jqXhr, textStatus, errorMessage) {
            console.log('Error: ' + errorMessage)
        }
    });

}

function topFunction() {
    $("html, body").animate({ scrollTop: 0 }, "slow");

}

function bottomFunction() { 
    $("html, body").animate({ 
        scrollTop: $(document).height()-$(window).height()
    }, "slow");

}