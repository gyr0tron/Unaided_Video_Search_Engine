// Increments the delay on each item.
$(".rolldown-list li").each(function () {
  var delay = $(this).index() / 3 + "s";
  $(this).css({
    webkitAnimationDelay: delay,
    mozAnimationDelay: delay,
    animationDelay: delay,
  });
});

$("#btnReload").click(function () {
  $("#myList").removeClass("rolldown-list");
  setTimeout(function () {
    $("#myList").addClass("rolldown-list");
  }, 1);
});
