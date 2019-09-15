const gulp = require('gulp');
const source = require('vinyl-source-stream');
const browserify = require('browserify');
const minify  = require('minify-stream');
const less = require('gulp-less');
const clean_css = require('gulp-clean-css');
const options = require('gulp-options');
const js_lint = require('gulp-jshint');
const gulp_if = require('gulp-if');

const output_dir = 'static';

const fast = options.has("fast");
if (fast) {
    console.log("no minification will be performed");
}

function js() {
    return browserify('assets/main.js')
        .bundle()
        .pipe(gulp_if(!fast, minify()))
        .pipe(source('bundled.main.js'))
        .pipe(gulp.dest(output_dir))
}

function lint() {
    return gulp.src(['assets/main.js'])
        .pipe(js_lint())
        .pipe(js_lint.reporter('jshint-stylish'))
        .pipe(js_lint.reporter('fail'));
}

function css() {
    return gulp.src('assets/style.less')
        .pipe(less())
        .pipe(gulp_if(!fast, clean_css()))
        .pipe(gulp.dest(output_dir))
}

function images() {
    return gulp.src('assets/images/*')
        .pipe(gulp.dest('static/images/'))
}

gulp.task('lint', function () {
    return lint();
});

gulp.task('js', function () {
    return js();
});

gulp.task('css', function () {
    return css();
});



gulp.task('images', function () {
    return images();
});

function watch() {
    gulp.watch(['assets/main.js'], {}, gulp.series('js'));
    gulp.watch(['assets/style.less'], {}, gulp.series('css'));
    gulp.watch(['assets/images/*'], {}, gulp.series('images'));
}

gulp.task('build', gulp.parallel('css', 'images', gulp.series('lint', 'js')));
gulp.task('default', gulp.series('build'));

exports.watch = gulp.series('build', watch);