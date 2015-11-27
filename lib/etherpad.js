// Send savefile to Etherpad defined in config, using etherpad-lite-client API

var api = require('etherpad-lite-client');
var fs  = require('fs');
var _config;
var _etherpad;

// Setup connection to etherpad
function setup(config) {
  _config = config;
  _etherpad = api.connect({
    apikey: _config.apikey,
    host:   _config.host,
    port:   _config.port,
  });
}

// Push content of savefile to configured etherpad
function _doUpdate(callback) {
  var contents = fs.readFileSync(_config.savefile);
  var args = {
    padID: _config.padID,
    text:  contents.toString(),
  };

  // TODO: Update content instead of just setting
  _etherpad.setText(args, function(error, data) {
    if (error) {
      // handle error using error.code and error.message
      console.log('ERROR: ');
      console.log(error);
    }

    if (typeof callback == 'function') { callback(); }
  });
}

function exitAction(callback) {
  _doUpdate(callback);
}

function timedAction() {
  _doUpdate();
}

// Engine must contain these two actions:
module.exports = {
  setup: setup,
  exitAction: exitAction,
  timedAction: timedAction,
};
