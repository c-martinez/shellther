#! /usr/bin/env node

var spawn  = require('child_process').spawn;
var fs     = require('fs');
var config = require('./config');
var engine = require('./lib/' + config.engine);

// Taken from: https://groups.google.com/forum/#!topic/nodejs/b9JdFrJQqn0
function shell(cmd, opts, callback) {
  process.stdin.pause();
  process.stdin.setRawMode(false);

  var child = spawn(cmd, opts, {
    stdio: 'inherit',
  });
  child.on('exit', function() {
    process.stdin.setRawMode(true);
    process.stdin.resume();
    engine.exitAction(function() {
      process.exit();
    });
  });

  return child;
}

var timer;
function triggerTimer() {
  if (!timer) {
    timer = setTimeout(function() {
      engine.timedAction();
      timer = null;
    }, timeout * 1000);
  }
}

var userArgs = process.argv.slice(2);
var savefile = userArgs[0];

if (savefile === undefined) {
  savefile = 'somefile.txt';
}

config.savefile = savefile;
engine.setup(config);

var timeout = 5;  // in seconds

shell('script', ['-f', savefile]);
fs.watch(savefile, triggerTimer);
