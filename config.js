var dummyConfig = {
  engine: 'dummy',
};

// Configuration for working with Etherpad
var etherpadConfig = {
  engine: 'etherpad',

  // API key of your etherpad (from APIKEY.txt)
  apikey: '',

  // Address where your etherpad is hosted
  host: 'localhost',

  // Port on which etherpad runs
  port: 9001,

  // Name of the target pad you want to write to
  padID: '',
};

// TODO: Add configurations for other engines (if available)

// TODO: export whichever configuration you would like to use
module.exports = dummyConfig;
// module.exports = etherpadConfig;
