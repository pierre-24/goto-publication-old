const gulp = require('gulp');
const source = require('vinyl-source-stream');
const browserify = require('browserify');
const minify  = require('minify-stream');
const less = require('gulp-less');
const clean_css = require('gulp-clean-css');

const output_dir = 'static';

function js() {
    return browserify('assets/main.js')
        .bundle()
        .pipe(minify())
        .pipe(source('bundled.main.js'))
        .pipe(gulp.dest(output_dir))
}

function css() {
    return gulp.src('assets/style.less')
        .pipe(less())
        .pipe(clean_css())
        .pipe(gulp.dest(output_dir))
}

gulp.task('minify', function () {
    return js();
});

gulp.task('css', function () {
    return css()
});

gulp.task('default', gulp.parallel('css', 'minify'));