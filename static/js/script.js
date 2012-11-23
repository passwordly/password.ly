
var passwordly = {};

passwordly.autocompleteIdentifier = function(cb) {

  $('#identifier').attr('autocomplete', 'off').typeahead({'source': cb});

};

$.fn.anychange = function (fn) {
  $(this).change(fn).keyup(fn).each(fn);
  return this;
};

$(function(){
  if ($('#copy-result').length) {
    ZeroClipboard.setMoviePath('static/swf/ZeroClipboard.swf');
    var clip = new ZeroClipboard.Client();
    clip.setText($('#result').val());
    clip.glue('copy-result', 'copy-result-container');
    $('#copy-result').click(function() {
      alert('js failed');
    });
  }

  $('#result').focus(function() {

    $('#result').select();
    // Delay selecting in case of browser reading the click
    setTimeout(function() {
      $('#result').select();
    }, 30);
  });
});
