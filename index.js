#! /usr/bin/env node

var spawn  = require('child_process').spawn;
var fs     = require('fs');

// Load config and desired engine
var config = require('./config');
var engine = require('./lib/' + config.engine);

// Trigger to call engine.timedAction every N seconds
var timer;
function triggerTimer() {
  if (!timer) {
    timer = setTimeout(function() {
      engine.timedAction();
      timer = null;
    }, timeout * 1000);
  }
}

// Taken from: https://groups.google.com/forum/#!topic/nodejs/b9JdFrJQqn0
// Start a terminal which logs output to given file and setup for engine
// functions to be called
function shellLogger(savefile) {
  process.stdin.pause();
  process.stdin.setRawMode(false);

  // Launch logging terminal
  var child = spawn('script', ['-f', savefile], {
    stdio: 'inherit',
  });

  // Setup engine.exitAction trigger
  child.on('exit', function() {
    process.stdin.setRawMode(true);
    process.stdin.resume();
    engine.exitAction(function() {
      process.exit();
    });
  });

  // Setup engine.timedAction trigger
  fs.watch(savefile, triggerTimer);
}

// Pass in savefile from command line (or use default: shellLog.txt)
var userArgs = process.argv.slice(2);
var savefile = userArgs[0];
if (savefile === undefined) {
  savefile = 'shellLog.txt';
}

// Configure engine
config.savefile = savefile;
engine.setup(config);

// Launch shell
var timeout = 5;  // in seconds
shellLogger(savefile);
