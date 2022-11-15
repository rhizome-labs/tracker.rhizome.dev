const colors = require('tailwindcss/colors')

module.exports = {
  content: ["./tracker_rhizome_dev/app/templates/**/*.{html,js}"],
  theme: {
    colors: {
      transparent: 'transparent',
      current: 'currentColor',
      black: '#0b0b0b',
      cyan: colors.cyan,
      white: colors.white,
      gray: colors.slate,
      green: colors.emerald,
      orange: colors.orange,
      red: colors.red,
      yellow: colors.yellow
    },
    extend: {
      opacity: {
        '85': '.85',
      }
    }
  },
  plugins: [],
}
