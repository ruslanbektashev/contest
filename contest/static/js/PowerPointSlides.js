$(".slide").css({opacity: 0, position: 'absolute', top: 0, height: 0, right: '-300px',left: 'unset', transition: '0.3s'});//display non
$('#slideslideIface1').css({opacity: 1, position: 'relative', height: 'auto', right: 0,left: 'unset'})

var $counter = 1;
var $ind = 0;
var $id;
var $flag = true;


$("#next_power_point_slide").on('click', function () {
    $counter = $counter + 1;
    $('.slide').each(function (index, element) {
        $id = '#slideslideIface' + index;
        if ($counter == index) {
            $($id).css({opacity: 1, position: 'relative', height: 'auto', left: 'unset', right: 0});//slidedown

        } else {
            $($id).css({opacity: 0, position: 'absolute', right: '-300px', left: 'unset', top: 0 , height: 0});//slideup
        }
        $ind = index;
    });
    $ind += 1
    $id = '#slideslideIface' + $ind;
    if ($ind == $counter) $($id).css({opacity: 1, position: 'relative', height: 'auto', right: 0, left: 'unset'});
    if ($ind < $counter) {
        $counter = $ind;
    }
});

$("#prev_power_point_slide").on('click', function () {
    if ($ind == $counter) $($id).css({opacity: 0, position: 'absolute', right: 'unset', left: '-300px', top: 0 , height: 0});
    if ($counter > 1) $counter = $counter - 1;
    $($('.slide').get().reverse()).each(function (index, element) {
        $id = '#slideslideIface' + index;
        if ($counter == index) {
            $($id).css({opacity: 1, position: 'relative', height: 'auto', left: 0, right: 'unset'});
        } else {
            $($id).css({opacity: 0, position: 'absolute', right: 'unset', left: '-300px', top: 0 , height: 0});
        }
    });
});

$('#start_power_point_slide').on('click', function () {
    $counter = 1;
    $(".slide").css({opacity: 0, position: 'absolute', top: 0, height: 0, right: '-300px',left: 'unset', transition: '0.3s'});
    $('#slideslideIface1').css({opacity: 1, position: 'relative', height: 'auto', left: 'unset', right: 0});
});
$('#end_power_point_slide').on('click', function () {
    $('.slide').each(function (index, element) {
        $counter = index + 1;
    });
    $ind = $counter;
    $id = '#slideslideIface' + $counter;
    $(".slide").css({opacity: 0, position: 'absolute', top: 0, height: 0, right: '-300px',left: 'unset', transition: '0.3s'});
    $($id).css({opacity: 1, position: 'relative', height: 'auto', left: 'unset', right: 0});
});

$('#Change_mode').on('click', function () {
    if ($flag == true) {
        $('.slide').each(function (index, element) {
            $id = '#slideslideIface' + index;
            $($id).css({opacity: 1, position: 'relative', height: 'auto', left: 'unset', right: 0});
            $ind = index;
        });
        $ind += 1;
        $id = '#slideslideIface' + $ind;
        $($id).css({opacity: 1, position: 'relative', height: 'auto', left: 'unset', right: 0})
        $(".hide_button").css("display", "none");
        $('#mode_view').removeClass('fa fa-file-text-o');
        $('#mode_view').addClass('fa fa-files-o');
        $flag = false;
    } else {
        $('#mode_view').removeClass('fa fa-files-o');
        $('#mode_view').addClass('fa fa-file-text-o');
        $(".hide_button").css("display", "block");
        $(".slide").css({opacity: 0, position: 'absolute', top: 0, height: 0, right: '-300px',left: 'unset', transition: '0.3s'});
        $('#slideslideIface1').css({opacity: 1, position: 'relative', height: 'auto', left: 'unset', right: 0});
        $counter = 1;
        $flag = true;
    }
});

