import { chromium } from 'playwright-core'

const EXEC = '/opt/pw-browsers/chromium-1194/chrome-linux/chrome'
const OUT = process.env.SHOT_DIR
const URL = 'http://localhost:4173/'

const browser = await chromium.launch({ executablePath: EXEC, args: ['--no-sandbox'] })
const page = await browser.newPage({ viewport: { width: 1280, height: 900 } })
const errors = []
page.on('console', m => { if (m.type() === 'error') errors.push(m.text()) })
page.on('pageerror', e => errors.push('PAGEERROR: ' + e.message))

await page.goto(URL, { waitUntil: 'networkidle' })
await page.waitForTimeout(400)

async function shot(name) {
  await page.screenshot({ path: `${OUT}/${name}.png`, fullPage: true })
  console.log('shot', name)
}
async function nav(label, name) {
  await page.getByRole('button', { name: label }).click()
  await page.waitForTimeout(350)
  await shot(name)
}

await shot('1-overview')
await nav('Theory & rank explorer', '2-theory')
await nav('Numeric proofs', '3-numeric')
await nav('Depth (multi-layer)', '4-depth')
await nav('Task families (live)', '5-families')
await nav('Haiku scaling sweep', '6-sweep')
await nav('Repo & reproduce', '7-repro')

console.log('CONSOLE_ERRORS', JSON.stringify(errors))
await browser.close()
