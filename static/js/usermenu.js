var userMenu;
var hoveringUserCircle;
var hoveringUserMenu;

$(document).ready(function() {
  userMenu = document.getElementById("usermenu");
  hoveringUserCircle = false;
  hoveringUserMenu = false;
});

function expandUserMenu() {
  userMenu.style.opacity = "1";
  userMenu.style.width = "220px";
  userMenu.style.height = "120px";
}

function collapseUserMenu() {
  userMenu.style.opacity = "0";
  userMenu.style.width = "0";
  userMenu.style.height = "0";
}

function hoverUser() {
  hoveringUserCircle = true;
  if (!hoveringUserMenu) {
    expandUserMenu();
  }
}

function leaveUser() {
  hoveringUserCircle = false;
  setTimeout(function(){
    if (!hoveringUserMenu) {
      collapseUserMenu();
    }
  }, 300);
}

function hoverUserMenu() {
  hoveringUserMenu = true;
  expandUserMenu();
}

function leaveUserMenu() {
  hoveringUserMenu = false;
  setTimeout(function(){
    if (!hoveringUserCircle) {
      collapseUserMenu();
    }
  }, 300);
}
