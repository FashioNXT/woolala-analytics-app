function deleteItem(button) {
    
    var url = null; 
    var deleteId = $(button).attr('name');
    if ( $(button).attr('id') == 'reportedPosts'){
        url = "delete_post/" + deleteId;
    } else if ( $(button).attr('id') == 'reportedUsers' ) {
        url = "delete_user/" + deleteId;
    }
    console.log(url)

    $.ajax( url , {
        type: 'DELETE',  // http method
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

// function scrollToAnchor(anchor){

//     var id = $(anhor).attr('href');
//     $('html,body').animate({scrollTop: $(id).offset().top}, 500);
//     // $('html,body').animate({
//     //     scrollTop: tag.offset().top
//     // },'slow');
// }

// $(".a[href^=#]").on('click', function(event) { 
//     event.preventDefault(); 
//     var name = $(this).attr('href'); 
//     var target = $('a[name="' + name.substring(1) + '"]'); 
//     $('html,body').animate({ scrollTop: $(target).offset().top }, 'slow'); 
// })