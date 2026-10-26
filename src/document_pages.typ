#import "style_tokens.typ": visual, typefaces
#import "block_renderers.typ": render-block

#let compose-page(page, page-number, page-count) = {
  let section-name = if "section" in page { page.section } else { "" }
  grid(
    columns: (1fr, auto),
    align: horizon,
    text(size: 7pt, weight: "bold", fill: visual.accent)[#upper(section-name)],
    text(font: typefaces.mono, size: 6.5pt, fill: visual.muted)[#page.id],
  )
  v(7mm)
  text(size: 21pt, weight: "bold", fill: visual.ink)[#page.title]
  if "subtitle" in page {
    v(1.5mm)
    text(size: 10pt, fill: visual.muted)[#page.subtitle]
  }
  v(6mm)
  for item in page.blocks {
    render-block(item)
    v(3mm)
  }
  v(1fr)
  line(length: 100%, stroke: 0.6pt + visual.rule)
  v(2mm)
  grid(
    columns: (1fr, auto),
    align: horizon,
    text(size: 6.5pt, fill: visual.muted)[#section-name],
    text(font: typefaces.mono, size: 6.5pt, fill: visual.ink)[#page-number / #page-count],
  )
}
