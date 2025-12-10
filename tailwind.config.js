/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // Anatomy-themed color palette
        'anatomy': {
          bone: '#E8DCC4',
          muscle: '#C41E3A',
          tendon: '#D4A574',
          ligament: '#8B7355',
          cartilage: '#A8D5BA',
          organ: '#8B4557',
        },
        // UI colors - dark theme for medical visualization
        'surface': {
          50: '#f8fafc',
          100: '#f1f5f9',
          200: '#e2e8f0',
          300: '#cbd5e1',
          400: '#94a3b8',
          500: '#64748b',
          600: '#475569',
          700: '#334155',
          800: '#1e293b',
          900: '#0f172a',
          950: '#020617',
        }
      },
      fontFamily: {
        'display': ['IBM Plex Sans', 'system-ui', 'sans-serif'],
        'mono': ['IBM Plex Mono', 'monospace'],
      },
    },
  },
  plugins: [],
}
