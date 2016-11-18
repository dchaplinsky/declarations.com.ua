module.exports = function(grunt) {

    grunt.initConfig({
        pkg: grunt.file.readJSON('package.json'),

        
         sass: {
            dist: {
                options: {
                    style: 'expanded'
                    //lineNumbers: true // for debug
                },
                files: {
                    'css/style.css': 'sass/style.scss',
                    'css/bi/style.css': 'sass/bi/style.scss',
                }
            }
        },

        watch: {
            grunt: {
                files: ['Gruntfile.js']
            },
            
            sass: {
                files: [
                    'sass/**/*.scss'
                ],
                tasks: ['sass', 'postcss']
            },
        },
        
        postcss: {
            options: {
              processors: [
                require('autoprefixer')({browsers: ['last 2 versions', 'ie 10']}),
              ]
            },
            dist: {
              src: 'css/style.css'
            }
        }, 

    });

    // load npm modules
    grunt.loadNpmTasks('grunt-contrib-sass');
    grunt.loadNpmTasks('grunt-contrib-watch');
    grunt.loadNpmTasks('grunt-postcss');

    // register tasks
    grunt.registerTask('default', ['sass', 'postcss',  'watch']);
    grunt.registerTask('jenkins', ['sass', 'postcss']);
};
