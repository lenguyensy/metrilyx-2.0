module.exports = {
  concat_app: {
    tasks: ['concat_sourcemap:app']
  },
  concat_app_dependencies: {
    tasks: ['concat_sourcemap:app_dependencies']
  },
  concat_test: {
    tasks: ['concat_sourcemap:test']
  }
};
