#import "src/style_tokens.typ": visual, typefaces
#import "src/document_pages.typ": compose-page

#let model = json(sys.inputs.at("book"))
#let document-info = model.document
#let page-spec = document-info.page
#let margins = page-spec.margin_mm

#set page(
  width: page-spec.width_mm * 1mm,
  height: page-spec.height_mm * 1mm,
  margin: (
    top: margins.top * 1mm,
    right: margins.right * 1mm,
    bottom: margins.bottom * 1mm,
    left: margins.left * 1mm,
  ),
  fill: visual.paper,
)
#set document(title: document-info.title)
#set text(font: typefaces.body, lang: document-info.language, size: 9.5pt, fill: visual.ink)
#set par(justify: false, leading: 0.52em, spacing: 0.55em)

#for (index, page) in model.pages.enumerate() [
  #compose-page(page, index + 1, model.pages.len())
  #if index < model.pages.len() - 1 { pagebreak() }
]
