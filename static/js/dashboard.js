/*function revertAGB() {
  // returning gamebox to original state
  $(this).removeClass("gameformbox");
  $(this).find("#gameform").addClass("invisible");
  $(this).data("viewingform", false);
  $(this).find(".gamelabel").show(100);
}*/

$( document ).ready(function() {
  $(".addgamebox").click(function() {
    if (! $(this).data("viewingform")) {
      // melt away gamelabel, display form
      $(this).addClass("gameformbox");
      $(this).find("#gameform").removeClass("invisible");
      $(this).data("viewingform", true);
      $(this).find(".gamelabel").hide(100);
    }
  });
});
