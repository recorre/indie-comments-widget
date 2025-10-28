import { nodeResolve } from '@rollup/plugin-node-resolve';
import { terser } from 'rollup-plugin-terser';
import commonjs from '@rollup/plugin-commonjs';

export default {
  input: 'src/widget.js',
  output: [
    {
      file: 'dist/comment-widget.js',
      format: 'es',
      sourcemap: true
    },
    {
      file: 'dist/comment-widget.min.js',
      format: 'es',
      sourcemap: true,
      plugins: [terser()]
    },
    {
      file: 'dist/comment-widget.umd.js',
      format: 'umd',
      name: 'CommentWidget',
      sourcemap: true
    },
    {
      file: 'dist/comment-widget.umd.min.js',
      format: 'umd',
      name: 'CommentWidget',
      sourcemap: true,
      plugins: [terser()]
    }
  ],
  plugins: [
    nodeResolve({
      browser: true,
      preferBuiltins: false
    }),
    commonjs()
  ],
  external: [],
  onwarn: function(warning) {
    // Suppress certain warnings
    if (warning.code === 'THIS_IS_UNDEFINED') return;
    console.warn(warning.message);
  }
};