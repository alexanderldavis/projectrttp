$(document).ready(function() {
  $(function() {
    $(document).on('click', function(e) {
        if (e.target.id === 'usercircle') {
          $('#usermenu').addClass('showusermenu');
          $('#usermenu').removeClass('hideusermenu');
        } else {
          $('#usermenu').removeClass('showusermenu');
          $('#usermenu').addClass('hideusermenu');
        }
    })
  });
});
