$(".slide").css("display", "none");
$('#slideslideIface1').slideDown(0);

var $counter = 1;
var $ind = 0;
var $id;
var $flag = true


$("#next_power_point_slide").on('click', function () {
    $counter = $counter + 1;
    $('.slide').each(function (index, element) {
        $id = '#slideslideIface' + index;
        if ($counter == index) {
            $($id).slideDown(300);
        } else {
            $($id).slideUp(300);
        }
        $ind = index;
    });
    $ind += 1
    $id = '#slideslideIface' + $ind;
    if ($ind == $counter) $($id).slideDown(300);
    if ($ind < $counter) {
        $counter = $ind;
    }
});

$("#prev_power_point_slide").on('click', function () {
    if ($ind == $counter) $($id).slideUp(300);
    if ($counter > 1) $counter = $counter - 1;
    $($('.slide').get().reverse()).each(function (index, element) {
        $id = '#slideslideIface' + index;
        if ($counter == index) {
            $($id).slideDown(300);
        } else {
            $($id).slideUp(300);
        }
    });
});

$('#start_power_point_slide').on('click', function () {
    $counter = 1
    $(".slide").css("display", "none");
    $('#slideslideIface1').slideDown(300);
});
$('#end_power_point_slide').on('click', function () {
    $counter = $counter
    $('.slide').each(function (index, element) {
        $counter = index + 1;
    });
    $id = '#slideslideIface' + $counter;
    $(".slide").css("display", "none");
    $($id).slideDown(300);
});

$('#Change_mode').on('click', function () {
    if ($flag == true) {
        $('.slide').each(function (index, element) {
            $id = '#slideslideIface' + index;
            $($id).slideDown(400);
            $ind = index;
        });
        $ind += 1
        $id = '#slideslideIface' + $ind;
        $($id).slideDown(200);
        $(".hide_button").css("display", "none");
        $('#mode_view').removeClass('fa fa-file-text-o');
        $('#mode_view').addClass('fa fa-files-o');
        $flag = false;
    } else {
        $('#mode_view').removeClass('fa fa-files-o');
        $('#mode_view').addClass('fa fa-file-text-o');
        $(".hide_button").css("display", "block");
        $(".slide").css("display", "none");
        $('#slideslideIface1').slideDown(0);
        $counter = 1;
        $flag = true;
    }
});

