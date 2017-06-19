$(document).ready(function() {
  $(function() {
    $(document).on('click', function(e) {
        if ($( event.target ).parents('#addgamebox').length) {
          $('#addgamebox').addClass("gameformbox");
          $('#addgamebox').find("#gameform").removeClass("invisible");
          $('#addgamebox').find(".gamelabel").hide();
        } else {
          $('#addgamebox').removeClass("gameformbox");
          $('#addgamebox').find("#gameform").addClass("invisible");
          $('#addgamebox').find(".gamelabel").show();
        }
    })
  });
});
