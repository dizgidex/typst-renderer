#import "style_tokens.typ": visual, typefaces

#let title-size(level) = if level == 1 { 18pt } else if level == 2 { 14pt } else { 11pt }

#let heading(data) = text(
  size: title-size(data.level),
  weight: "bold",
  fill: visual.ink,
)[#data.text]

#let paragraph(data) = text(
  size: 9.5pt,
  fill: visual.ink,
)[#data.text]

#let list-content(data) = {
  let entries = data.items.map(item => [#item])
  if data.ordered {
    enum(..entries)
  } else {
    list(..entries)
  }
}

#let callout(data) = {
  let tone-color = if data.tone == "tip" {
    visual.tip
  } else if data.tone == "caution" {
    visual.caution
  } else {
    visual.note
  }
  block(
    width: 100%,
    fill: tone-color,
    stroke: (left: 2pt + visual.accent),
    radius: 2mm,
    inset: (x: 4mm, y: 3mm),
  )[
    #text(size: 7pt, weight: "bold", fill: visual.accent)[#upper(data.tone)]
    #v(1mm)
    #text(size: 9.5pt, weight: "bold", fill: visual.ink)[#data.title]
    #v(1mm)
    #text(size: 9pt, fill: visual.ink)[#data.text]
  ]
}

#let fact-card(data) = block(
  width: 100%,
  fill: visual.surface,
  stroke: 0.7pt + visual.rule,
  radius: 2mm,
  inset: (x: 4mm, y: 3mm),
)[
  #text(size: 7pt, weight: "bold", fill: visual.accent)[#upper(data.label)]
  #v(1mm)
  #text(size: 12pt, weight: "bold", fill: visual.ink)[#data.value]
  #if "detail" in data [
    #v(1mm)
    #text(size: 8pt, fill: visual.muted)[#data.detail]
  ]
]

#let relationship-node(label) = block(
  width: 100%,
  height: 16mm,
  fill: visual.surface,
  stroke: 0.8pt + visual.accent,
  radius: 2mm,
  inset: 2mm,
)[
  #align(center + horizon)[#text(size: 8pt, weight: "bold", fill: visual.ink)[#label]]
]

#let relationship-connector(label) = block(width: 18mm)[
  #align(center)[#text(size: 6pt, fill: visual.muted)[#label]]
  #align(center)[#text(size: 12pt, weight: "bold", fill: visual.accent)[→]]
]

#let relationship-diagram(data) = {
  let cells = data.nodes.enumerate().map(((index, label)) => {
    if index < data.relations.len() {
      (relationship-node(label), relationship-connector(data.relations.at(index)))
    } else {
      (relationship-node(label),)
    }
  }).flatten()
  grid(
    columns: (1fr, auto) * data.relations.len() + (1fr,),
    gutter: 1.5mm,
    align: center + horizon,
    ..cells,
  )
}

#let render-block(data) = {
  if data.type == "heading" {
    heading(data)
  } else if data.type == "paragraph" {
    paragraph(data)
  } else if data.type == "list" {
    list-content(data)
  } else if data.type == "callout" {
    callout(data)
  } else if data.type == "fact_card" {
    fact-card(data)
  } else {
    relationship-diagram(data)
  }
}
