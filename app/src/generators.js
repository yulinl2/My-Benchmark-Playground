// In-browser reimplementations of the seven NL task generators, for live
// preview. These mirror the Python generators in src/nl/{task_generator,
// extra_tasks}.py in STRUCTURE and answer logic; the surface strings differ
// (JS PRNG != Python PRNG), so they illustrate the task shape, not the exact
// committed instances. Every generator returns {task, prompt, answer, meta}.

function mulberry32(a) {
  return function () {
    a |= 0; a = (a + 0x6D2B79F5) | 0
    let t = Math.imul(a ^ (a >>> 15), 1 | a)
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296
  }
}
const rng = seed => mulberry32(seed >>> 0)
const ri = (r, n) => Math.floor(r() * n)
const choice = (r, arr) => arr[ri(r, arr.length)]
function shuffle(r, arr) {
  const a = arr.slice()
  for (let i = a.length - 1; i > 0; i--) { const j = ri(r, i + 1);[a[i], a[j]] = [a[j], a[i]] }
  return a
}
function sample(r, arr, k) { return shuffle(r, arr).slice(0, k) }
function code(r) {
  const C = '0123456789ABCDEFGHJKLMNPQRSTUVWXYZ'
  return Array.from({ length: 3 }, () => C[ri(r, C.length)]).join('')
}

export const WORDS = ('mango cedar violet quartz harbor lantern willow cobalt ember marble pewter ' +
  'saffron thicket clover bramble nectar gravel cinder tundra zephyr almond brisket cobweb dapple').split(' ')
const REAL_CITIES = ('Lisbon Cairo Oslo Tokyo Lima Accra Hanoi Quito Riga Doha Sofia Tunis Minsk ' +
  'Dakar Amman Bogota Manila Vienna Nassau Maputo').split(' ')
const BASE_NAMES = 'abcdefghijklmnopqrstuvwxyz'.split('')
const cityPool = n => { const p = REAL_CITIES.slice(); let i = 0; while (p.length < n) p.push('Sector' + String(i++).padStart(4, '0')); return p.slice(0, Math.max(n, REAL_CITIES.length)) }
const namePool = n => { const p = BASE_NAMES.slice(); let i = 0; while (p.length < n) p.push('v' + String(i++).padStart(3, '0')); return p }

export function gather(N, seed = 0) {
  const r = rng(seed + 101)
  const items = Array.from({ length: N }, () => choice(r, WORDS))
  const order = shuffle(r, [...Array(N).keys()])
  const lines = items.map((w, i) => `[${i + 1}] ${w}`).join('\n')
  const prompt = `You are given a list of labeled lines and an output order.\nLines:\n${lines}\n\nOutput order (line numbers): ${order.map(o => o + 1).join(', ')}\n\nTask: print the CONTENTS of the lines in exactly the given output order, one word per line, nothing else.`
  return { task: 'gather', prompt, answer: order.map(o => items[o]).join('\n'), meta: { N } }
}

export function mqar(N, k, seed = 0) {
  const r = rng(seed + 202)
  const pool = cityPool(N)
  const cities = sample(r, pool, k)
  const codes = {}; cities.forEach(c => codes[c] = code(r))
  const pad = shuffle(r, pool.filter(c => !cities.includes(c)))
  let facts = cities.map(c => [c, codes[c]])
  pad.slice(0, N - k).forEach(c => facts.push([c, code(r)]))
  facts = shuffle(r, facts)
  const factLines = facts.map(([c, v]) => `- The access code for ${c} is ${v}.`).join('\n')
  const q = shuffle(r, cities.slice())
  const questions = q.map((c, i) => `${i + 1}. access code for ${c}?`).join('\n')
  const prompt = `Use only the facts below.\nFacts:\n${factLines}\n\nQuestions:\n${questions}\n\nAnswer with one line per question as 'N. CODE', nothing else.`
  return { task: 'mqar', prompt, answer: q.map((c, i) => `${i + 1}. ${codes[c]}`).join('\n'), meta: { N: facts.length, k } }
}

export function chain(N, L, seed = 0) {
  const r = rng(seed + 303)
  N = Math.max(N, L + 1)
  const pool = namePool(N)
  const cv = sample(r, pool, L + 1)
  const literal = 10 + ri(r, 90)
  const stmts = []
  for (let i = 0; i < cv.length - 1; i++) stmts.push(`Let ${cv[i]} = ${cv[i + 1]}.`)
  stmts.push(`Let ${cv[cv.length - 1]} = ${literal}.`)
  const others = shuffle(r, pool.filter(n => !cv.includes(n)))
  others.slice(0, N - (L + 1)).forEach(n => stmts.push(`Let ${n} = ${10 + ri(r, 90)}.`))
  const body = shuffle(r, stmts).join('  ')
  return { task: 'chain', prompt: `${body}\n\nQuestion: What is the integer value of ${cv[0]}? Answer with only the integer.`, answer: String(literal), meta: { N, L } }
}

export function selectiveCopy(N, keepRate = 0.5, seed = 0) {
  const r = rng(seed + 404)
  const items = Array.from({ length: N }, () => choice(r, WORDS))
  const flags = Array.from({ length: N }, () => r() < keepRate)
  if (!flags.some(Boolean)) flags[ri(r, N)] = true
  const lines = items.map((w, i) => `[${i + 1}] ${w} -- ${flags[i] ? 'KEEP' : 'DROP'}`).join('\n')
  const prompt = `Below are labeled items, each marked KEEP or DROP.\n${lines}\n\nTask: output the words marked KEEP, in their original order, one per line, nothing else.`
  return { task: 'selective_copy', prompt, answer: items.filter((_, i) => flags[i]).join('\n'), meta: { N, kept: flags.filter(Boolean).length } }
}

export function sortByKey(N, seed = 0) {
  const r = rng(seed + 505)
  const items = Array.from({ length: N }, () => choice(r, WORDS))
  const keys = sample(r, [...Array(9000).keys()].map(x => x + 1000), N)
  const lines = items.map((w, i) => `${w} : ${keys[i]}`).join('\n')
  const order = [...Array(N).keys()].sort((a, b) => keys[a] - keys[b])
  const prompt = `Each line is 'word : key'.\n${lines}\n\nTask: output the words sorted by key in ASCENDING order, one per line, nothing else.`
  return { task: 'sort_by_key', prompt, answer: order.map(i => items[i]).join('\n'), meta: { N } }
}

export function kvLastwrite(N, nKeys, nQueries, seed = 0) {
  const r = rng(seed + 606)
  const keys = cityPool(nKeys).slice(0, nKeys)
  const last = {}, log = []
  const order = shuffle(r, [...Array(nKeys).keys()])
  for (let idx = 0; idx < N; idx++) {
    const k = idx < nKeys ? keys[order[idx]] : keys[ri(r, nKeys)]
    const v = code(r); last[k] = v; log.push([k, v])
  }
  const logLines = log.map(([k, v]) => `set ${k} = ${v}`).join('\n')
  const qk = sample(r, keys, nQueries)
  const questions = qk.map((k, i) => `${i + 1}. current value of ${k}?`).join('\n')
  const prompt = `This is a log of assignments; a later 'set' OVERRIDES an earlier one for the same name. Use only this log.\n${logLines}\n\nQuestions (give the CURRENT value):\n${questions}\n\nAnswer one line per question as 'N. VALUE', nothing else.`
  return { task: 'kv_lastwrite', prompt, answer: qk.map((k, i) => `${i + 1}. ${last[k]}`).join('\n'), meta: { N, n_keys: nKeys, n_queries: nQueries } }
}

export function multihopMap(domain, t, seed = 0) {
  const r = rng(seed + 707)
  const names = namePool(domain).slice(0, domain)
  const perm = shuffle(r, names)
  const f = {}; names.forEach((n, i) => f[n] = perm[i])
  const pairs = shuffle(r, names.map(n => [n, f[n]]))
  const table = pairs.map(([a, b]) => `${a} -> ${b}`).join('; ')
  const start = choice(r, names)
  let cur = start; for (let i = 0; i < t; i++) cur = f[cur]
  const prompt = `Mapping (each name maps to exactly one name): ${table}.\n\nStart at ${start} and apply the mapping ${t} times. Answer with only the final name.`
  return { task: 'multihop_map', prompt, answer: cur, meta: { domain, t } }
}

export const FAMILIES = {
  gather: { fn: gather, knobs: [['N', 6, 40, 12]], blurb: 'Reorder N lines by an explicit output order. Optimal attention is the permutation P_π (rank N).' },
  mqar: { fn: (p, s) => mqar(p.N, p.k, s), knobs: [['N', 10, 60, 20], ['k', 2, 16, 6]], blurb: 'In-context dictionary: N facts, k queried. Optimal attention: a partial permutation (rank k). Associative recall.' },
  chain: { fn: (p, s) => chain(p.N, p.L, s), knobs: [['N', 6, 40, 16], ['L', 2, 16, 5]], blurb: 'Resolve a variable through an L-step pointer chain among N assignments. Composition of L one-hot hops.' },
  selective_copy: { fn: (p, s) => selectiveCopy(p.N, 0.5, s), knobs: [['N', 6, 40, 12]], blurb: 'Output the KEEP-flagged items in order. Partial permutation (rank = #kept).' },
  sort_by_key: { fn: (p, s) => sortByKey(p.N, s), knobs: [['N', 5, 32, 10]], blurb: 'Reorder items by an in-context numeric key. Optimal attention is the argsort permutation (rank N).' },
  kv_lastwrite: { fn: (p, s) => kvLastwrite(p.N ?? 3 * p.n_keys, p.n_keys, Math.min(p.n_queries, p.n_keys), s), knobs: [['n_keys', 4, 24, 8], ['n_queries', 1, 8, 3]], blurb: 'Last-write-wins log of N=3·n_keys assignments; report the current value per key. Recall with overwrites.' },
  multihop_map: { fn: (p, s) => multihopMap(p.domain, p.t, s), knobs: [['domain', 6, 40, 12], ['t', 1, 16, 4]], blurb: 'Apply an in-context permutation map t times. Deep pointer composition.' },
}
