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
      $(this).data("expanded", false);
      $(this).css('height', '');
      $(this).css('width', '');
      $(".newspaperbox").hover(hoverNP, hoverNPNon);
    } else {
      $(this).data("expanded", true);
      $(this).css({
        'height' : '30em',
        'width' : '90%'
      });
      $(this).hover(hoverNPNon);
    }
  });
});
