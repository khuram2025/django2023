$('document').ready(function($) {
  $('body').append('<div id="fi_message"></div>');

  // HIDE MESSAGE ON CLICK
  $('body').on('click', '.fi_simple', function(){
    var el = $(this);
    el.slideUp(200);

    setTimeout(function(){
      el.remove();
    }, 800);
  });



  // MAKE FAVORITE BUTTON
  $('body').on('click', '.fi_make_favorite, .fi_save_favorite', function(){
    var rel = $(this).attr('rel');

    if($(this).hasClass('fi_save')) {
      var isSave = 1;
      var data_string = 'isSave=1&item_id='+ rel ;
    } else {
      var isSave = 0;
      var data_string = 'item_id='+ rel ;
    }

    var element = $(this);
    // Future update, when mark as favorite, do action on same item even if it is muliple times. Require looping bellow.
    //var element = $('.fi_save_favorite[rel="' + rel + '"]');
    var msg_box = $('#fi_message');


    if(isSave == 0) {
      element.find('span').animate({'margin-left': '20px'}, 200, 'linear');
    }


    $.ajax({
      type: "POST",
      datatype: "json",
      url: fi_favorite_url,
      data: data_string,
      cache: false,
      error: function(req, err){ console.log('ERROR on AJAX: ' + err); },

      success: function(data) {
        //console.log(data);  // show data in case of problem

        var data = $.parseJSON(data);


        // AVAILABLE: data['title'], data['message'], data['allow_message'], data['is_favorite'], data['item_title'], data['item_price'], data['item_img'], data['item_url']
        console.log(data);

        if(data && data['max_reached'] != 1) {
          if(isSave == 1) {
            element.find('span').text(data['title']);
          }

          element.prop('title', data['title']);
          element.toggleClass('is_favorite');

          if(isSave == 0) {
            element.find('span').animate({'margin-left': '-20px'}, 0);
            element.find('span').animate({'margin-left': '0px'}, 200, 'linear');
          }

          // IF LISTING IS NOT FAVORITE, REMOVE IT FROM LIST
          if( data['is_favorite'] == 0 ) {
            $('.fi_item_' + rel).slideUp(200, function() { 
              if($('.fi_item:visible').length == 0) {
                $('<div class="fi_empty" style="display:none;">' + fi_empty + '</div>').appendTo('#fi_list_items.fi_user_items').slideDown(200);
              } 
            });
          } else {
            fi_add_to_list(rel, data['item_title'], data['item_img'], data['item_price'], data['item_url']);
          }
        }


        // PRINT MESSAGE SECTION
        if(data && data['allow_message'] == 1) {
          var s_class =  Math.floor(Math.random() * 10000).toString();
          msg_box.append('<div class="fi_simple fi' + s_class + '">' + data['message'] + '</div>');

          setTimeout(function() {
            var t_el = $('.fi' + s_class);
            t_el.slideUp(200);

            setTimeout(function(){
              t_el.remove();
            }, 800);
          }, 3000);
        }
      }
    });
  });



  // REMOVE FROM LIST BUTTON
  $('body').on('click', '.fi_list_remove', function(){
    var rel = $(this).attr('rel');
    var data_string = 'item_remove_id='+ rel ;
    var element = $(this).parent().parent();
    var msg_box = $('#fi_message');

    $.ajax({
      type: "POST",
      datatype: "json",
      url: fi_favorite_url,
      data: data_string,
      cache: false,
      error: function(req, err){ console.log('ERROR on AJAX: ' + err); },

      success: function(data) {
        var data = $.parseJSON(data);

        // debug
        // console.log(data);
        // AVAILABLE: data['message'], data['allow_message']

        element.slideUp(200, function() { 
          if($('.fi_item:visible').length == 0) {
            $('<div class="fi_empty" style="display:none;">' + fi_empty + '</div>').appendTo('#fi_list_items.fi_user_items').slideDown(200);
          } 
        });

        $('.fi_fav_' + rel).removeClass('is_favorite');


        // PRINT MESSAGE SECTION
        if(data['allow_message'] == 1) {
          var s_class =  Math.floor(Math.random() * 10000).toString();
          msg_box.append('<div class="fi_simple fi' + s_class + '">' + data['message'] + '</div>');

          setTimeout(function() {
            var t_el = $('.fi' + s_class);
            t_el.slideUp(200);

            setTimeout(function(){
              t_el.remove();
            }, 800);
          }, 3000);
        }
      }
    });
  });



  // FUNCTION TO ADD NEW ENTRY INTO FAVORITE LIST VIA AJAX
  function fi_add_to_list(item_id, item_title, item_img, item_price, item_url) {
    if(!$('#fi_list_items.fi_user_items .fi_item_' + item_id).length) {
      $('#fi_list_items.fi_user_items').append('<div class="fi_item fi_item_' + item_id + '" style="display:none;"> <div class="fi_left"> <a class="fi_img-link" href="' + item_url + '"> <img src="' + item_img + '" title="' + item_title + '" alt="' + item_title + '"> </a> </div> <div class="fi_right"> <div class="fi_top"> <a href="' + item_url + '">' + item_title + '</a> </div> <div class="fi_bottom">' + item_price + '</div> </div> <div class="fi_tool"> <span class="fi_list_remove" title="Remove from list" rel="' + item_id + '"></span> </div> </div>');
      $('.fi_item_' + item_id).slideDown(200);
    } else {
      $('.fi_item_' + item_id).slideDown(200);
    }

    $('#fi_list_items.fi_user_items').find('.fi_empty').remove();
  }



  // EDIT LIST IN USER ACCOUNT
  $('body').on('click', '.fi_list_edit', function(){
    var rel = $(this).attr('rel');
    var name = $(this).siblings('a').text();

    $('input.fi_new_name').val(name);
    $('input[name="edit_action"]').val(1);
    $('input[name="edit_list_id"]').val(rel);
    $('#fi_user_new_list').addClass('edit_now');

    if($(this).parent().parent().find('.fi_current').hasClass('fi_active')) {
      $('input[name="fi_new_list_current"]').prop('checked', true);
    } else {
      $('input[name="fi_new_list_current"]').prop('checked', false);
    }

    if($(this).parent().parent().find('.fi_notification').hasClass('fi_active')) {
      $('input[name="fi_new_list_notification"]').prop('checked', true);
    } else {
      $('input[name="fi_new_list_notification"]').prop('checked', false);
    }

    $('html, body').animate({ scrollTop: $('#fi_user_new_list').offset().top - 100 }, 500);
  });
});