var hoverA = function() {
  $(this).find(".alabel").css({
    'height' : '100%',
    'background-color' : 'rgba(0,0,0,.4)',
    'transition' : '.2s'
  });
}

var hoverANon = function() {
  $(this).find(".alabel").css({
    'height' : '7em',
    'background-color' : 'rgba(0,0,0,.7)',
    'transition' : '.8s'
  });
}

$( document ).ready(function() {

  $(".assignmentbox").hover(hoverA,hoverANon);

  // Clicking on assignment box expands it to reveal its contents. Clicking again contracts it
  $(".assignmentbox").click(function() {
    if ($(this).data("expanded")) {
      // Contracting
      $('.assignmentbox').each(function() {
        $(this).removeClass("invisible");
        $(this).css('height', '');
      });
      $(this).data("expanded", false);
      $(this).removeClass("fullassignment");
      $(".alabel").removeClass("invisible");
      $(".alabel").css('height', '');
    } else {
      // Expanding clicked assignmentbox, hiding other
      let curBox = this;
      $('.assignmentbox').each(function() {
        if (this !== curBox) {
          $(this).addClass("invisible");
          $(this).css('height', '0');
        }
        console.log(this);
      });
      $(this).data("expanded", true);
      $(this).addClass("fullassignment");
      $(".alabel").css('height', '100%');
      $(this).find(".alabel").addClass("invisible");
    }
  });
});
