# Body components

The body is a plain HTML fragment. Everything below is already styled by
`scripts/build_pdf.py`. Do not add `<style>` blocks or new colours; the palette
guard rail will fail the build.

## Sections

```html
<h1>1. Where it stands</h1>          <!-- numbered section, navy 28px -->
<h1 class="fresh">7. Checklist</h1>  <!-- same, forced onto a new page -->
<h2>Before</h2>                      <!-- sub-section, navy 22px -->
<h3>Baseline to measure against</h3> <!-- minor heading, purple 17px -->
<p class="meta">Audited on 6 September 2026. Source: two page .docx.</p>
```

## Paragraphs and emphasis

```html
<p>Body copy. <strong>Bold is navy</strong> and used for the phrase that matters.</p>
<p class="pinned">Engineering Management &nbsp;|&nbsp; Team Leadership</p>  <!-- large navy line -->
```

## Callout (purple left rule, lilac fill)

```html
<div class="callout">
<p><strong>What this document has to do.</strong> One paragraph framing every judgement below.</p>
</div>
```

## Verdict / scorecard table

```html
<table>
<thead><tr><th class="num">#</th><th>Section</th><th>Verdict</th><th>Note</th></tr></thead>
<tbody>
<tr><td class="num">1</td><td>Headline</td><td class="fail">Fail</td><td>Why, in one line.</td></tr>
<tr><td class="num">2</td><td>Summary</td><td class="warn">Needs work</td><td>Why.</td></tr>
<tr><td class="num">3</td><td>Languages</td><td class="pass">Pass</td><td>Why.</td></tr>
</tbody>
</table>
```

`pass` renders purple, `warn`/`fail` render bold navy. No red or green: they are off palette.

## Metric table

```html
<table>
<thead><tr><th>Metric</th><th>Value</th><th>Read</th></tr></thead>
<tbody><tr><td>Pages</td><td>2</td><td>Target is 1.</td></tr></tbody>
</table>
```

## Ranked list

```html
<ol class="priority">
<li><strong>Fix the biggest thing first.</strong> Why it matters, in two sentences.</li>
</ol>
```

## Before / after or paste-ready text

```html
<h2>Before</h2>
<pre>Old text exactly as it appears.</pre>
<h2>After</h2>
<pre>New text, ready to paste.</pre>
```

Escape `<`, `>` and `&` inside `<pre>`.

## Checklist (empty tick boxes)

```html
<table class="checklist">
<thead><tr><th class="box"></th><th>Task</th><th>Time</th></tr></thead>
<tbody><tr><td class="box"></td><td>Apply the new headline</td><td>5 min</td></tr></tbody>
</table>
```

## Grouped paragraphs

```html
<div class="skills"><p><strong>Management:</strong> ...</p><p><strong>Technical:</strong> ...</p></div>
```
