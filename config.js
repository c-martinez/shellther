var dummyConfig = {
  engine: 'dummy',
};

// Configuration for working with Etherpad
var etherpadConfig = {
  engine: 'etherpad',

  // API key of your etherpad (from APIKEY.txt)
  apikey: 'e792c32e44952f8d24c2cabe35bf36a12003d04726d3579c36f5a1d00569c81c',

  // Address where your etherpad is hosted
  host: 'localhost',

  // Port on which etherpad runs
  port: 9001,

  // Name of the target pad you want to write to
  padID: 'scshell-test',
};

// TODO: Add configurations for other engines (if available)

// TODO: export whichever configuration you would like to use
// module.exports = dummyConfig;
module.exports = etherpadConfig;
