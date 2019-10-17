var gulp = require('gulp');
var cp = require('child_process');
var ts = require('gulp-typescript');
var argv = require('yargs').argv;
var _ = require('lodash');
var tsProject = ts.createProject('tsconfig.json');

gulp.task('build', function() {
    return tsProject.src()
        .pipe(ts(tsProject))
        .pipe(gulp.dest('./'));
});

gulp.task('run', function(done) {
    var args = _.map(argv, function(v, p) { return '--' + p + '=' + v }).join(' ');
    cp.execSync('node ./ThirdPartyNoticesGen.js ' + args, {
        stdio: 'inherit'
    });
    done();
});

gulp.task('generate', gulp.series('build', 'run'));
