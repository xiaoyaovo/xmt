const DEFAULT_SPACING = {
  xs: '4px',
  sm: '8px',
  md: '16px',
  lg: '24px',
  xl: '40px'
}

const DEFAULT_FONT_WEIGHT = {
  regular: '400',
  medium: '500',
  semibold: '600'
}

function createPalette({
  accent,
  accentHover,
  accentSoft,
  accent2,
  highlight,
  glow,
  surface,
  surface2,
  text,
  muted,
  border
}) {
  return {
    accent,
    'accent-hover': accentHover,
    'accent-soft': accentSoft,
    accent2,
    highlight,
    glow,
    surface,
    'surface-2': surface2,
    text,
    muted,
    border
  }
}

export const brands = {
  editorial: {
    id: 'editorial',
    name: '编辑感',
    subtitle: '深海蓝与杂志感排版',
    colors: createPalette({
      accent: '#102542',
      accentHover: '#17345d',
      accentSoft: 'rgba(16, 37, 66, 0.08)',
      accent2: '#ff7a59',
      highlight: '#c6ff6a',
      glow: 'rgba(198, 255, 106, 0.24)',
      surface: '#ffffff',
      surface2: '#eef3f8',
      text: '#0f1723',
      muted: '#5f6b7a',
      border: 'rgba(16, 37, 66, 0.12)'
    }),
    borderRadius: { xs: '4px', sm: '8px', md: '16px', lg: '24px', pill: '999px' },
    spacing: DEFAULT_SPACING,
    fontFamily: '"Avenir Next", "Segoe UI", sans-serif',
    fontWeight: DEFAULT_FONT_WEIGHT,
    boxShadow: {
      card: '0 18px 46px rgba(16, 37, 66, 0.10)',
      elevated: '0 28px 90px rgba(16, 37, 66, 0.16)',
      focus: '0 0 0 3px rgba(16, 37, 66, 0.16)'
    }
  },
  terminal: {
    id: 'terminal',
    name: '终端感',
    subtitle: '深底高亮与偏工具化气质',
    colors: createPalette({
      accent: '#c6ff6a',
      accentHover: '#b1ef55',
      accentSoft: 'rgba(198, 255, 106, 0.16)',
      accent2: '#7ed7ff',
      highlight: '#f4ff8f',
      glow: 'rgba(126, 215, 255, 0.20)',
      surface: '#10151d',
      surface2: '#1a2230',
      text: '#edf4ff',
      muted: '#9bb0cc',
      border: 'rgba(255, 255, 255, 0.08)'
    }),
    borderRadius: { xs: '2px', sm: '6px', md: '12px', lg: '18px', pill: '999px' },
    spacing: DEFAULT_SPACING,
    fontFamily: '"IBM Plex Sans", "Segoe UI", sans-serif',
    fontWeight: DEFAULT_FONT_WEIGHT,
    boxShadow: {
      card: '0 16px 40px rgba(0, 0, 0, 0.24)',
      elevated: '0 28px 86px rgba(0, 0, 0, 0.34)',
      focus: '0 0 0 3px rgba(198, 255, 106, 0.22)'
    }
  },
  apple: {
    id: 'apple',
    name: 'Apple 感',
    subtitle: '纯净蓝与雾白表面',
    colors: createPalette({
      accent: '#0071e3',
      accentHover: '#0077ed',
      accentSoft: 'rgba(0, 113, 227, 0.10)',
      accent2: '#5ac8fa',
      highlight: '#9df0ff',
      glow: 'rgba(90, 200, 250, 0.22)',
      surface: '#ffffff',
      surface2: '#f5f5f7',
      text: '#1d1d1f',
      muted: '#6e6e73',
      border: 'rgba(29, 29, 31, 0.08)'
    }),
    borderRadius: { xs: '2px', sm: '6px', md: '10px', lg: '18px', pill: '980px' },
    spacing: DEFAULT_SPACING,
    fontFamily: '-apple-system, BlinkMacSystemFont, "SF Pro Display", "Helvetica Neue", sans-serif',
    fontWeight: { regular: '400', medium: '500', semibold: '700' },
    boxShadow: {
      card: '0 2px 14px rgba(0, 0, 0, 0.06)',
      elevated: '0 18px 52px rgba(0, 0, 0, 0.10)',
      focus: '0 0 0 4px rgba(0, 113, 227, 0.20)'
    }
  },
  carbon: {
    id: 'carbon',
    name: 'Carbon 感',
    subtitle: '工业感结构与 IBM Plex',
    colors: createPalette({
      accent: '#0f62fe',
      accentHover: '#0353e9',
      accentSoft: 'rgba(15, 98, 254, 0.12)',
      accent2: '#42be65',
      highlight: '#a7f0ba',
      glow: 'rgba(66, 190, 101, 0.20)',
      surface: '#ffffff',
      surface2: '#f4f4f4',
      text: '#161616',
      muted: '#525252',
      border: '#e0e0e0'
    }),
    borderRadius: { xs: '0', sm: '0', md: '0', lg: '0', pill: '16px' },
    spacing: DEFAULT_SPACING,
    fontFamily: '"IBM Plex Sans", "Helvetica Neue", sans-serif',
    fontWeight: DEFAULT_FONT_WEIGHT,
    boxShadow: {
      card: '0 1px 2px rgba(0, 0, 0, 0.10)',
      elevated: '0 18px 48px rgba(0, 0, 0, 0.16)',
      focus: '0 0 0 2px #0f62fe inset'
    }
  },
  fluent: {
    id: 'fluent',
    name: 'Fluent 感',
    subtitle: '微软式清爽蓝与柔和中性灰',
    colors: createPalette({
      accent: '#0f6cbd',
      accentHover: '#115ea3',
      accentSoft: 'rgba(15, 108, 189, 0.10)',
      accent2: '#66c7f4',
      highlight: '#b8e8ff',
      glow: 'rgba(102, 199, 244, 0.22)',
      surface: '#ffffff',
      surface2: '#f5f5f5',
      text: '#242424',
      muted: '#616161',
      border: '#d1d1d1'
    }),
    borderRadius: { xs: '2px', sm: '4px', md: '4px', lg: '8px', pill: '9999px' },
    spacing: DEFAULT_SPACING,
    fontFamily: '"Segoe UI", -apple-system, sans-serif',
    fontWeight: { regular: '400', medium: '600', semibold: '700' },
    boxShadow: {
      card: '0 2px 4px rgba(0, 0, 0, 0.14), 0 0 2px rgba(0, 0, 0, 0.12)',
      elevated: '0 16px 42px rgba(0, 0, 0, 0.14)',
      focus: '0 0 0 2px #0f6cbd'
    }
  },
  primer: {
    id: 'primer',
    name: 'Primer 感',
    subtitle: 'GitHub 式冷白面板与理性蓝',
    colors: createPalette({
      accent: '#0969da',
      accentHover: '#0860c8',
      accentSoft: 'rgba(9, 105, 218, 0.10)',
      accent2: '#2da44e',
      highlight: '#b7f0c1',
      glow: 'rgba(45, 164, 78, 0.18)',
      surface: '#ffffff',
      surface2: '#f6f8fa',
      text: '#1f2328',
      muted: '#656d76',
      border: '#d0d7de'
    }),
    borderRadius: { xs: '4px', sm: '6px', md: '6px', lg: '12px', pill: '2em' },
    spacing: DEFAULT_SPACING,
    fontFamily: '-apple-system, "Segoe UI", "Mona Sans", sans-serif',
    fontWeight: DEFAULT_FONT_WEIGHT,
    boxShadow: {
      card: '0 1px 0 rgba(31, 35, 40, 0.04), 0 1px 3px rgba(66, 74, 83, 0.12)',
      elevated: '0 16px 40px rgba(140, 149, 159, 0.18)',
      focus: '0 0 0 3px rgba(9, 105, 218, 0.28)'
    }
  },
  stripe: {
    id: 'stripe',
    name: 'Stripe 感',
    subtitle: '高对比紫蓝与金融产品感',
    colors: createPalette({
      accent: '#635bff',
      accentHover: '#5851e8',
      accentSoft: 'rgba(99, 91, 255, 0.12)',
      accent2: '#00d4ff',
      highlight: '#9bf1ff',
      glow: 'rgba(0, 212, 255, 0.20)',
      surface: '#ffffff',
      surface2: '#f7f9fc',
      text: '#1a1f36',
      muted: '#6b7280',
      border: 'rgba(99, 91, 255, 0.14)'
    }),
    borderRadius: { xs: '4px', sm: '8px', md: '14px', lg: '22px', pill: '9999px' },
    spacing: DEFAULT_SPACING,
    fontFamily: '"Soehne", "Avenir Next", "Segoe UI", sans-serif',
    fontWeight: { regular: '400', medium: '500', semibold: '700' },
    boxShadow: {
      card: '0 16px 44px rgba(99, 91, 255, 0.10)',
      elevated: '0 28px 90px rgba(99, 91, 255, 0.16)',
      focus: '0 0 0 4px rgba(99, 91, 255, 0.20)'
    }
  },
  linear: {
    id: 'linear',
    name: 'Linear 感',
    subtitle: '冷黑灰与锐利产品感',
    colors: createPalette({
      accent: '#5e6ad2',
      accentHover: '#4c57c1',
      accentSoft: 'rgba(94, 106, 210, 0.12)',
      accent2: '#a78bfa',
      highlight: '#ddd6fe',
      glow: 'rgba(167, 139, 250, 0.18)',
      surface: '#ffffff',
      surface2: '#f7f7f8',
      text: '#0f1013',
      muted: '#6b6f76',
      border: 'rgba(15, 16, 19, 0.10)'
    }),
    borderRadius: { xs: '4px', sm: '8px', md: '12px', lg: '16px', pill: '999px' },
    spacing: DEFAULT_SPACING,
    fontFamily: '"Inter", "Segoe UI", sans-serif',
    fontWeight: { regular: '400', medium: '500', semibold: '700' },
    boxShadow: {
      card: '0 10px 28px rgba(15, 16, 19, 0.08)',
      elevated: '0 22px 58px rgba(15, 16, 19, 0.14)',
      focus: '0 0 0 3px rgba(94, 106, 210, 0.18)'
    }
  },
  material: {
    id: 'material',
    name: 'Material 感',
    subtitle: 'Google 式紫调与柔和层次',
    colors: createPalette({
      accent: '#6750a4',
      accentHover: '#7c65bf',
      accentSoft: 'rgba(103, 80, 164, 0.12)',
      accent2: '#ffb4ab',
      highlight: '#ffd8d2',
      glow: 'rgba(255, 180, 171, 0.18)',
      surface: '#fffbfe',
      surface2: '#f3edf7',
      text: '#1c1b1f',
      muted: '#49454f',
      border: 'rgba(103, 80, 164, 0.14)'
    }),
    borderRadius: { xs: '4px', sm: '8px', md: '12px', lg: '16px', pill: '100px' },
    spacing: DEFAULT_SPACING,
    fontFamily: '"Roboto", -apple-system, sans-serif',
    fontWeight: DEFAULT_FONT_WEIGHT,
    boxShadow: {
      card: '0 1px 2px rgba(0, 0, 0, 0.30), 0 1px 3px rgba(0, 0, 0, 0.15)',
      elevated: '0 18px 48px rgba(0, 0, 0, 0.18)',
      focus: '0 0 0 3px rgba(103, 80, 164, 0.24)'
    }
  },
  spotify: {
    id: 'spotify',
    name: 'Spotify 感',
    subtitle: '深色音乐产品感与霓虹绿',
    colors: createPalette({
      accent: '#1db954',
      accentHover: '#1ed760',
      accentSoft: 'rgba(29, 185, 84, 0.16)',
      accent2: '#7dd3fc',
      highlight: '#d9f99d',
      glow: 'rgba(29, 185, 84, 0.22)',
      surface: '#121212',
      surface2: '#1e1e1e',
      text: '#f5f5f5',
      muted: '#b3b3b3',
      border: 'rgba(255, 255, 255, 0.08)'
    }),
    borderRadius: { xs: '4px', sm: '8px', md: '16px', lg: '24px', pill: '999px' },
    spacing: DEFAULT_SPACING,
    fontFamily: '"Circular Std", "Avenir Next", "Segoe UI", sans-serif',
    fontWeight: { regular: '400', medium: '500', semibold: '700' },
    boxShadow: {
      card: '0 16px 42px rgba(0, 0, 0, 0.26)',
      elevated: '0 30px 96px rgba(0, 0, 0, 0.34)',
      focus: '0 0 0 3px rgba(29, 185, 84, 0.24)'
    }
  },
  claude: {
    id: 'claude',
    name: 'Claude 感',
    subtitle: '温暖米白与低饱和棕橙',
    colors: createPalette({
      accent: '#c56f4d',
      accentHover: '#b5603f',
      accentSoft: 'rgba(197, 111, 77, 0.12)',
      accent2: '#8c6a5d',
      highlight: '#f6d8c9',
      glow: 'rgba(197, 111, 77, 0.18)',
      surface: '#faf7f2',
      surface2: '#f2ece3',
      text: '#2f241f',
      muted: '#7c6e66',
      border: 'rgba(108, 88, 76, 0.14)'
    }),
    borderRadius: { xs: '6px', sm: '10px', md: '18px', lg: '26px', pill: '999px' },
    spacing: DEFAULT_SPACING,
    fontFamily: '"Source Serif 4", "Avenir Next", "Segoe UI", serif',
    fontWeight: { regular: '400', medium: '500', semibold: '600' },
    boxShadow: {
      card: '0 12px 34px rgba(108, 88, 76, 0.10)',
      elevated: '0 24px 72px rgba(108, 88, 76, 0.14)',
      focus: '0 0 0 3px rgba(197, 111, 77, 0.16)'
    }
  },
  vercel: {
    id: 'vercel',
    name: 'Vercel 感',
    subtitle: '黑白极简与冷静中性灰',
    colors: createPalette({
      accent: '#111111',
      accentHover: '#2b2b2b',
      accentSoft: 'rgba(17, 17, 17, 0.06)',
      accent2: '#666666',
      highlight: '#d4d4d4',
      glow: 'rgba(17, 17, 17, 0.12)',
      surface: '#ffffff',
      surface2: '#fafafa',
      text: '#111111',
      muted: '#666666',
      border: '#eaeaea'
    }),
    borderRadius: { xs: '4px', sm: '6px', md: '8px', lg: '12px', pill: '9999px' },
    spacing: DEFAULT_SPACING,
    fontFamily: '"Geist Sans", "Inter", "Segoe UI", sans-serif',
    fontWeight: DEFAULT_FONT_WEIGHT,
    boxShadow: {
      card: '0 2px 4px rgba(0, 0, 0, 0.06), 0 1px 2px rgba(0, 0, 0, 0.04)',
      elevated: '0 18px 48px rgba(0, 0, 0, 0.10)',
      focus: '0 0 0 3px rgba(17, 17, 17, 0.14)'
    }
  }
}

export const BRAND_PRESETS = Object.values(brands).map(({ id, name, subtitle }) => ({
  id,
  name,
  subtitle
}))

export const DEFAULT_BRAND_ID = 'editorial'

export function getBrandTokens(brandId = DEFAULT_BRAND_ID) {
  return brands[brandId] || brands[DEFAULT_BRAND_ID]
}

export const activeBrandTokens = getBrandTokens(DEFAULT_BRAND_ID)
