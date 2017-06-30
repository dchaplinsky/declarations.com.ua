module.exports = function(grunt) {
    grunt.initConfig({
        pkg: grunt.file.readJSON('package.json'),

        svgstore: {
            logos: {
                files: {
                    'declarations_site/catalog/static/images/svg-images-sprite.svg': 'images-svg/*.svg'
                    //use like <span class="svg-image logo"><svg preserveAspectRatio="xMidYMid" focusable="false"><use xlink:href="{{ static("images/svg-images-sprite.svg#bihus-logo") }}"></use></svg></span>
                }
            }
        },

        watch: {
            grunt: {
                files: ['Gruntfile.js']
            },

            svgstore: {
                files: [
                    'images-svg/*.svg'
                ],
                tasks: [ 'svgstore']
            }
        }
    });

    // load npm modules
    grunt.loadNpmTasks('grunt-svgstore');
    grunt.loadNpmTasks('grunt-contrib-watch');

    // register tasks
    grunt.registerTask('default', ['svgstore', 'watch']);
    grunt.registerTask('jenkins', ['svgstore']);
};
