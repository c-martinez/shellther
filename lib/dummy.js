// DUMMY engine -- you can build your own engine based on this one

// Setup should be explicitly call
function setup(config) {
  console.log('Your SETUP code goes here');
}

// This function gets executed on exit
function exitAction() {
  console.log('Your EXIT code goes here');
}

// This function gets executed after N seconds of inactivity
function timedAction() {
  console.log('Your INTERMEDIATE code goes here');
}

// Engine must contain these actions:
module.exports = {
  setup: setup,
  exitAction: exitAction,
  timedAction: timedAction,
};
