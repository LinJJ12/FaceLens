/**
 * ECharts 自定义主题 — 基于 FaceLens 中性灰设计令牌。
 *
 * canvas 无法解析 CSS 变量（如 `var(--color-ink)` 会被当字面量），
 * 因此在这里注册两套与 theme.css 令牌保持一致的固定值主题：
 * - `facelens`      浅色（默认）
 * - `facelens-dark` 深色（html.dark 时）
 *
 * 用法：
 *   registerFacelensChartThemes()          // 首次 echarts.init 前调用一次
 *   echarts.init(el, currentChartTheme())  // 主题切换时需 dispose 后以新主题重建
 */
import * as echarts from 'echarts'

// 与 theme.css 的 zinc 中性灰令牌一一对应
const TOKENS = {
  light: {
    surface: '#ffffff',
    ink: '#09090b',
    muted: '#71717a',
    border: '#e4e4e7',
    fill: '#f4f4f5',
  },
  dark: {
    surface: '#161618',
    ink: '#f4f4f5',
    muted: '#a1a1aa',
    border: '#27272a',
    fill: '#1d1d21',
  },
}

// 数据语义色板（与 Element Plus 状态色一致）
const PALETTE = ['#5470c6', '#91cc75', '#fac858', '#ee6666', '#73c0de', '#3ba272', '#fc8452', '#9a60b4']

let registered = false

function buildTheme(t) {
  return {
    backgroundColor: 'transparent',
    color: PALETTE,
    textStyle: { color: t.ink },
    legend: { textStyle: { color: t.muted } },
    tooltip: {
      backgroundColor: t.surface,
      borderColor: t.border,
      borderWidth: 1,
      padding: [8, 12],
      textStyle: { color: t.ink },
      extraCssText: 'box-shadow: 0 4px 12px rgba(0,0,0,0.12); border-radius: 8px;',
    },
    categoryAxis: {
      axisLine: { lineStyle: { color: t.border } },
      axisTick: { lineStyle: { color: t.border } },
      axisLabel: { color: t.muted },
      splitLine: { show: false, lineStyle: { color: t.border } },
      nameTextStyle: { color: t.muted },
    },
    valueAxis: {
      axisLine: { show: false, lineStyle: { color: t.border } },
      axisTick: { show: false },
      axisLabel: { color: t.muted },
      splitLine: { lineStyle: { color: t.border } },
      nameTextStyle: { color: t.muted },
    },
    timeAxis: {
      axisLine: { lineStyle: { color: t.border } },
      axisLabel: { color: t.muted },
      splitLine: { lineStyle: { color: t.border } },
    },
    logAxis: {
      axisLine: { lineStyle: { color: t.border } },
      axisLabel: { color: t.muted },
      splitLine: { lineStyle: { color: t.border } },
    },
    radar: {
      axisName: { color: t.muted },
      splitLine: { lineStyle: { color: t.border } },
      splitArea: { show: false },
      axisLine: { lineStyle: { color: t.border } },
    },
    calendar: {
      itemStyle: { color: t.fill, borderColor: t.border },
      dayLabel: { color: t.muted },
      monthLabel: { color: t.muted },
      yearLabel: { color: t.muted },
    },
    dataZoom: {
      backgroundColor: 'transparent',
      dataBackgroundColor: t.fill,
      fillerColor: 'rgba(113,113,122,0.2)',
      handleColor: t.border,
      textStyle: { color: t.muted },
    },
  }
}

export function registerFacelensChartThemes() {
  if (registered) return
  echarts.registerTheme('facelens', buildTheme(TOKENS.light))
  echarts.registerTheme('facelens-dark', buildTheme(TOKENS.dark))
  registered = true
}

/** 当前应使用的主题名（跟随 html.dark） */
export function currentChartTheme() {
  if (typeof document !== 'undefined' && document.documentElement.classList.contains('dark')) {
    return 'facelens-dark'
  }
  return 'facelens'
}

/** 在 JS（canvas/内联样式）里读取主题令牌的实际值 */
export function chartToken(name) {
  const dark = currentChartTheme() === 'facelens-dark'
  // 支持 '--color-surface' 与 'surface' 两种写法
  const key = name.replace(/^--(color-)?/, '')
  return (dark ? TOKENS.dark : TOKENS.light)[key] ?? cssVarRaw(name)
}

function cssVarRaw(name) {
  if (typeof window === 'undefined') return ''
  return getComputedStyle(document.documentElement).getPropertyValue(name).trim()
}
