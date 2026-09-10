/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // 核心色板 - KONTUR 纸感 CRM 风格
        ink: 'rgb(var(--ink) / <alpha-value>)',
        paper: 'rgb(var(--paper) / <alpha-value>)',
        card: 'rgb(var(--card) / <alpha-value>)',
        line: 'rgb(var(--line) / <alpha-value>)',
        green: 'rgb(var(--green) / <alpha-value>)',
        amber: 'rgb(var(--amber) / <alpha-value>)',
        
        // 功能色
        success: 'rgb(var(--success) / <alpha-value>)',
        warning: 'rgb(var(--warning) / <alpha-value>)',
        danger: 'rgb(var(--danger) / <alpha-value>)',
        destructive: 'rgb(var(--destructive) / <alpha-value>)',
        
        // 背景色
        'bg-primary': 'rgb(var(--background) / <alpha-value>)',
        'bg-secondary': 'rgb(var(--background-secondary) / <alpha-value>)',
        'bg-tertiary': 'rgb(var(--background-tertiary) / <alpha-value>)',
        'bg-sidebar': 'rgb(var(--ink) / <alpha-value>)',
        
        // 文字色
        foreground: 'rgb(var(--ink) / <alpha-value>)',
        'foreground-secondary': 'rgb(102, 102, 102)',
        'foreground-muted': 'rgb(161, 161, 170)',
      },
      fontSize: {
        'xs': ['10px', { lineHeight: '1.5' }],
        'sm': ['11px', { lineHeight: '1.5' }],
        'base': ['13px', { lineHeight: '1.5' }],
        'lg': ['14px', { lineHeight: '1.5' }],
        'xl': ['16px', { lineHeight: '1.5' }],
        '2xl': ['18px', { lineHeight: '1.25' }],
        '3xl': ['20px', { lineHeight: '1.25' }],
        'page-title': ['22px', { lineHeight: '1.25', fontFamily: 'Instrument Serif' }],
        'metric-value': ['28px', { lineHeight: '1.25' }],
      },
      fontFamily: {
        serif: ['Instrument Serif', 'Georgia', 'serif'],
        sans: ['Archivo', '-apple-system', 'BlinkMacSystemFont', 'PingFang SC', 'Microsoft YaHei', 'sans-serif'],
        mono: ['IBM Plex Mono', 'Fira Code', 'Consolas', 'monospace'],
      },
      spacing: {
        '1': '4px',
        '2': '8px',
        '3': '12px',
        '4': '16px',
        '5': '20px',
        '6': '24px',
        '8': '32px',
        '10': '40px',
        '12': '48px',
      },
      borderRadius: {
        'sm': '4px',
        'md': '6px',
        'lg': '8px',
        'xl': '12px',
        'full': '9999px',
      },
      boxShadow: {
        'sm': '0 1px 0 rgb(218, 213, 200, 0.5)',
        'md': '0 2px 4px rgb(218, 213, 200, 0.3)',
        'lg': '0 4px 8px rgb(218, 213, 200, 0.2)',
      },
      letterSpacing: {
        'tight': '-0.02em',
        'normal': '0',
        'wide': '0.08em',
        'wider': '0.14em',
        'widest': '0.22em',
      },
    },
  },
  plugins: [],
}
