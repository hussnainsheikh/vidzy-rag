import { existsSync, readFileSync, readdirSync, statSync } from "node:fs"
import { join, relative, resolve } from "node:path"

const root = resolve(import.meta.dirname, "../..")
const knowledgeRoot = join(root, "knowledge")
const errors = []
const warnings = []
const validateOriginalSources = process.env.VALIDATE_ORIGINAL_SOURCES === "true"

function readJsonl(relativePath, { optional = false } = {}) {
  const absolute = join(root, relativePath)
  if (optional && !existsSync(absolute)) return []
  const lines = readFileSync(absolute, "utf8").split(/\r?\n/)
  const rows = []
  lines.forEach((line, index) => {
    if (!line.trim()) return
    try {
      rows.push(JSON.parse(line))
    } catch (error) {
      errors.push(`${relativePath}:${index + 1}: invalid JSON (${error.message})`)
    }
  })
  return rows
}

function uniqueIds(rows, label) {
  const seen = new Set()
  for (const row of rows) {
    if (!row.id || typeof row.id !== "string") {
      errors.push(`${label}: row without a string id`)
      continue
    }
    if (seen.has(row.id)) errors.push(`${label}: duplicate id ${row.id}`)
    seen.add(row.id)
  }
  return seen
}

function listFiles(directory) {
  const files = []
  for (const entry of readdirSync(directory)) {
    const absolute = join(directory, entry)
    if (statSync(absolute).isDirectory()) files.push(...listFiles(absolute))
    else files.push(absolute)
  }
  return files
}

const facts = readJsonl("knowledge/metadata/facts.jsonl", { optional: true })
const questions = readJsonl("knowledge/metadata/questions.jsonl")
const sources = readJsonl("knowledge/metadata/sources.jsonl", { optional: true })
const factIds = uniqueIds(facts, "facts")
uniqueIds(questions, "questions")
uniqueIds(sources, "sources")

const allowedStatuses = new Set(["verified", "probable", "uncertain"])
const factById = new Map(facts.map((fact) => [fact.id, fact]))
const normalizedFacts = new Map()

for (const fact of facts) {
  if (!allowedStatuses.has(fact.status)) errors.push(`fact ${fact.id}: invalid status`)
  if (!new Set(["public", "internal"]).has(fact.scope)) errors.push(`fact ${fact.id}: invalid scope`)
  if (!Array.isArray(fact.evidence) || fact.evidence.length === 0) {
    errors.push(`fact ${fact.id}: missing evidence`)
  } else {
    for (const evidence of fact.evidence) {
      if (!evidence.path) {
        errors.push(`fact ${fact.id}: missing evidence path`)
      } else if (!existsSync(join(root, evidence.path))) {
        const message = `fact ${fact.id}: original evidence path unavailable in standalone repository: ${evidence.path}`
        if (validateOriginalSources) errors.push(message)
        else warnings.push(message)
      }
      if (!evidence.type) errors.push(`fact ${fact.id}: evidence without type`)
    }
  }
  const normalized = String(fact.fact ?? "").toLowerCase().replace(/[^a-z0-9]+/g, " ").trim()
  if (normalizedFacts.has(normalized)) {
    errors.push(`duplicate fact text: ${normalizedFacts.get(normalized)} and ${fact.id}`)
  }
  normalizedFacts.set(normalized, fact.id)
}

for (const question of questions) {
  if (question.scope !== "public") errors.push(`question ${question.id}: scope must be public`)
  if (question.status !== "verified") errors.push(`question ${question.id}: status must be verified`)
  if (!Array.isArray(question.aliases)) errors.push(`question ${question.id}: aliases must be an array`)
  if (!Array.isArray(question.source_fact_ids) || question.source_fact_ids.length === 0) {
    errors.push(`question ${question.id}: no source_fact_ids`)
    continue
  }
  for (const id of question.source_fact_ids) {
    if (facts.length === 0) continue
    if (!factIds.has(id)) {
      errors.push(`question ${question.id}: unknown fact ${id}`)
      continue
    }
    const fact = factById.get(id)
    if (fact.scope !== "public" || fact.status !== "verified") {
      errors.push(`question ${question.id}: fact ${id} is not verified public knowledge`)
    }
  }
}

for (const source of sources) {
  if (!source.path) {
    errors.push(`source ${source.id}: missing path`)
  } else if (!existsSync(join(root, source.path))) {
    const message = `source ${source.id}: original path unavailable in standalone repository: ${source.path}`
    if (validateOriginalSources) errors.push(message)
    else warnings.push(message)
  }
}

const knowledgeFiles = listFiles(knowledgeRoot)
const markdownFiles = knowledgeFiles.filter((file) => file.endsWith(".md"))
for (const file of markdownFiles) {
  const text = readFileSync(file, "utf8")
  const rel = relative(root, file)
  if (!text.startsWith("# ")) errors.push(`${rel}: missing descriptive H1`)
  if (rel.startsWith("knowledge/internal/") && !text.includes("\n## Evidence\n")) {
    errors.push(`${rel}: missing Evidence section`)
  }
}

const combined = knowledgeFiles.map((file) => readFileSync(file, "utf8")).join("\n")
const secretPatterns = [
  /-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----/i,
  /\b(?:sk|pk)_(?:live|test)_[A-Za-z0-9]{16,}\b/,
  /\bgh[pousr]_[A-Za-z0-9]{20,}\b/,
  /\bAKIA[0-9A-Z]{16}\b/,
  /\b(?:password|passwd|api[_-]?key|access[_-]?key|secret|token)\s*[=:]\s*["']?[A-Za-z0-9+/_.-]{12,}["']?/i,
  /postgres(?:ql)?:\/\/[^\s:@/]+:[^\s@/]+@/i,
]
for (const pattern of secretPatterns) {
  if (pattern.test(combined)) errors.push(`knowledge files match secret pattern ${pattern}`)
}

const publicFiles = markdownFiles.filter((file) => file.includes(`${join("knowledge", "public")}`))
const internalMarkers = [
  /hard[- ]coded.{0,40}(?:secret|credential|signing key)/i,
  /(?:missing|unchecked).{0,40}(?:ownership|authorization)/i,
  /(?:security|authentication).{0,30}(?:bypass|finding)/i,
]
for (const file of publicFiles) {
  const text = readFileSync(file, "utf8")
  for (const marker of internalMarkers) {
    if (marker.test(text)) errors.push(`${relative(root, file)}: matched a private-content pattern`)
  }
}

const statusCounts = facts.reduce((acc, fact) => {
  acc[fact.status] = (acc[fact.status] ?? 0) + 1
  return acc
}, {})

if (warnings.length) warnings.forEach((warning) => console.warn(`WARN ${warning}`))
if (errors.length) {
  errors.forEach((error) => console.error(`ERROR ${error}`))
  process.exitCode = 1
} else {
  console.log(`Validated ${facts.length} facts, ${questions.length} questions, ${sources.length} sources, and ${markdownFiles.length} Markdown files.`)
  console.log(`Fact status counts: ${JSON.stringify(statusCounts)}`)
}
