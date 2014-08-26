module.exports = function(grunt) {
  'use strict';
  var BASE_TASK_DIR = './tasks/options/';

  //dynamically load tasks
  var fs = require('fs');
  var dirs = fs.readdirSync(BASE_TASK_DIR);
  var options = {pkg: grunt.file.readJSON('package.json')};
  dirs.forEach(function(fileName) {
    var key = fileName.substr(0, fileName.indexOf('.js')),
    option = require(BASE_TASK_DIR + fileName);

    options[key] = option;
  });


  // Project configuration
  require('jit-grunt')(grunt);
  grunt.initConfig(options);


  // Default task
  grunt.registerTask('test', ['clean:debug', 'concurrent:concat_app', 'concurrent:concat_app_dependencies', 'concurrent:concat_test', 'karma:ci']);
  grunt.registerTask('default', ['test']);
};
