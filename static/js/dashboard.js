$( document ).ready(function() {

  $(".addgamebox").click(function() {
    if ($(this).data("viewingform")) {
      // returning gamebox to original state
      $(this).find(".gamelabel").css('opacity', '');
      $(this).css('border', '');
      $(this).css('box-shadow', '');
      $(this).find("#gameform").addClass("invisible");
      $(this).css('background', '');
      $(this).data("viewingform", false);
      $(this).find(".gamelabel").show(100);
    } else {
      // melt away gamelabel, display form
      //$(this).find(".gamelabel").css('opacity', '0');
      $(this).css('box-shadow', 'inset 0 0 8px black');
      $(this).css('border', '4px solid rgb(34, 34, 34)');
      $(this).css('background','white');
      $(this).find("#gameform").removeClass("invisible");
      $(this).data("viewingform", true);
      $(this).find(".gamelabel").hide(100);
    }
  });
});
