# Rutgers Statistics PhD qualifying exam — format & study notes

Everything here is compiled from **publicly available** Rutgers Statistics
department pages. The exams themselves are behind an authenticated SharePoint
repo (see below) and are not reproduced here.

## When & who

- Taken by all PhD students **before the start of their second year**.
- The material is drawn from the **first-year PhD course sequence**.

## Structure

The qualifying exam has **two parts**:

1. **In-class written exam** — covers **mathematical statistics** and
   **probability theory**.
2. **Take-home exam** — covers **applied statistics**.

In this repo these map to the `part` values:

| Exam component                | `part` value  |
| ----------------------------- | ------------- |
| Probability theory            | `probability` |
| Mathematical statistics       | `math-stat`   |
| Applied (take-home)           | `applied`     |

## Typical topic areas

Based on the first-year PhD curriculum, expect questions on:

**Probability**
- Measure-theoretic probability, distributions, expectations
- Modes of convergence (a.s., in probability, in distribution, $L^p$)
- Laws of large numbers, central limit theorems
- Characteristic functions, moment generating functions
- Conditional expectation, martingales (program-dependent)

**Mathematical statistics**
- Sufficiency, completeness, exponential families
- Point estimation: MLE, method of moments, UMVUE, Cramér–Rao
- Hypothesis testing: Neyman–Pearson, likelihood ratio, UMP tests
- Confidence sets, asymptotic theory (consistency, asymptotic normality)
- Bayesian inference, decision theory

**Applied statistics (take-home)**
- Linear and generalized linear models, regression diagnostics
- ANOVA / experimental design
- Data analysis, model selection, and written interpretation

> Treat the topic list as a study scaffold, not an official syllabus. Refine it
> against the actual past exams once you've transcribed them — `build_bank.py`
> prints a topic-coverage summary to help you see what's well represented.

## Where the official past exams live

- **Past PhD Exams & Solutions** (landing page):
  <https://statistics.rutgers.edu/graduate-academics/past-phd-exams>
- The page links to a **Rutgers-authenticated SharePoint** repository:
  `https://rutgersconnect.sharepoint.com/sites/stat-ms_phd_past_exams`
  → *Go to documents* (requires a Rutgers NetID login).
- Related: **Past MS Exams & Solutions**:
  <https://statistics.rutgers.edu/graduate-academics/past-ms-exams-solution>

Because that repository requires login, the exams **cannot be auto-scraped**.
Download the PDFs while logged in, drop them in `exams/pdfs/`, and use the
transcription workflow in the top-level `README.md`.

## Sources

- Past PhD Exams & Solutions — <https://statistics.rutgers.edu/graduate-academics/past-phd-exams>
- PhD Degree Program — <https://statistics.rutgers.edu/graduate-academics/phd-degree-program>
- PhD Typical Plan — <https://statistics.rutgers.edu/graduate-academics/phd-typical-plan>
