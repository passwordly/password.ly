
var passwordly = {};

passwordly.autocompleteIdentifier = function(cb) {

  $('#identifier').attr('autocomplete', 'off').typeahead({'source': cb});

};

(function() {
  var cache = {};

  passwordly.checkPassword = function(username, password, cb) {


    if (cache[password]) {
      if (cache[password].busy) {
        // @todo: Consider a retry here
        cache[password].callbacks.push(cb);
      }else{
        cb(cache[password].result ? cache[password] : null);
      }
    }else{
      // Mark the result as 'busy fetching'
      cache[password] = {'busy': true, 'callbacks': [cb]};
      
      // Go fetch the result for the password
      $.post('/user/get-sites', {
        'username': username,
        'password': password
      }, function(data, textStatus) {
        if (textStatus == 'success') {
          var callbacks = cache[password].callbacks;
          cache[password] = data;

          for (var k = 0; k < callbacks.length; k++) {
            callbacks[k](data.result ? data : null);
          }
        }
      }, 'json');
    }

  };
})();

$.fn.anychange = function (fn) {
  $(this).change(fn).keyup(fn).each(fn);
  return this;
};

$(function(){
  if ($('#copy-result').length) {
    ZeroClipboard.setMoviePath('/static/swf/ZeroClipboard.swf');
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


/*** 
 * Existing password
 **/
$('#existing-password').anychange(function() {
  var $self = $(this);
  var value = $self.val();

  // Callback might be called instantly and reverse this
  $('#existing-password-result').html('<i class="icon-ban-circle" style="color:#666; font-size:18px;"></i>');

  passwordly.checkPassword($('span#username').text(), value, function(result) {
    if ($self.val() != value) {
      return;
    }

    if (result) {
      $('#existing-password-result').html('<i class="icon-ok-circle" style="color:#494; font-size:18px;"></i>');
    }
  });

});
