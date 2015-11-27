var api = require('etherpad-lite-client');
var fs  = require('fs');
var _config;

function setup(config) {
  _config = config;
}

// This action gets executed on exit
function exitAction(callback) {
  console.log('Etherpad engine EXIT function === START');

  var etherpad = api.connect({
    apikey: _config.apikey,
    host:   _config.host,
    port:   _config.port,
  });
  var contents = fs.readFileSync(_config.savefile);

  console.log('Using config:');
  console.log(_config);
  console.log('contents.toString()');
  console.log(contents.toString());

  var args = {
    padID: _config.padID,
    text:  contents.toString(),
  };

  etherpad.setText(args, function(error, data) {
    if (error) {
      // handle error using error.code and error.message
      console.log('ERROR: ');
      console.log(error);
    }

    console.log('Push OK');
    callback();
  });

  console.log('Etherpad engine EXIT function === END');
}

// This action gets executed after N seconds of inactivity
function timedAction() {
  // do nothing -- submit content to etherpad only on exit
  // console.log('Your INTERMEDIATE callback could be called here');
}

console.log('Etherpad engine loaded!');

// Engine must contain these two actions:
module.exports = {
  setup: setup,
  exitAction: exitAction,
  timedAction: timedAction,
};
