var hoverNP = function() {
  $(this).find(".nplabel").css({
    'height' : '100%',
    'background-color' : 'rgba(0,0,0,.4)',
    'transition' : '.2s'
  });
}

var hoverNPNon = function() {
  $(this).find(".nplabel").css({
    'height' : '4em',
    'background-color' : 'rgba(0,0,0,.7)',
    'transition' : '.8s'
  });
}

$( document ).ready(function() {

  $(".newspaperbox").hover(hoverNP,hoverNPNon);

  // Clicking on newspaper box expands it to reveal its contents. Clicking again contracts it
  $(".newspaperbox").click(function() {
    if ($(this).data("expanded")) {
      // Contracting
      $('.newspaperbox').each(function(i, obj) {
        $(this).removeClass("invisible");
      });
      $(this).data("expanded", false);
      $(this).removeClass("fullarticle");
      $(this).css('height', '');
      $(this).css('width', '');
      $(".nplabel").removeClass("invisible");
      $(".nplabel").css({
        'height' : '4em',
      });
    } else {
      // Expanding clicked newspperbox, hiding others
      $('.newspaperbox').each(function(i, obj) {
        $(this).addClass("invisible");
      });
      $(this).removeClass("invisible");
      $(this).data("expanded", true);
      $(this).addClass("fullarticle");
      $(".nplabel").css({
        'height' : '100%',
      });
      $(this).find(".nplabel").addClass("invisible");
    }
  });
});
