$( document ).ready(function() {

  $(".addgamebox").click(function() {
    if ($(this).data("viewingform")) {
      // returning gamebox to original state
      $(this).find(".gamelabel").css('opacity', '');
      $(this).find("#gameform").addClass("invisible");
      console.log($(this).find("#gameform"));
      $(this).css('background','');
      $(this).data("viewingform", false);
    } else {
      // melt away gamelabel, display form
      $(this).find(".gamelabel").css('opacity', '0');
      $(this).css('background','white');
      $(this).find("#gameform").removeClass("invisible");
      console.log($(this).find("#gameform"));
      $(this).data("viewingform", true);
    }
  });
});
