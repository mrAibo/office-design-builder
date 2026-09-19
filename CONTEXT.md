# Office Design Builder Context

## Language

**Semantic specification**: Compact versioned JSON describing content intent and layout roles without implementation code or absolute coordinates.

**Style fingerprint**: Normalized design evidence extracted from a reference: palette, typography, geometry, density, motif, and canvas.

**Design family**: A coherent set of design rules that can accept token overrides without becoming a fixed template.

**Composable layout**: Renderer-owned arrangement of semantic slots such as title, body, chart, image, and callout.

**Template-preserving edit**: Mutation that retains the source Office theme, masters, styles, numbering, sections, and native element semantics where possible.

**Image reconstruction**: Creation of editable Office elements inspired by a raster reference. It is not the insertion of that image as a page-sized background.

**Structural verification**: Machine check that an Office package opens and contains expected editable elements and content.

**Visual verification**: Render-based review for overflow, overlap, clipping, font substitution, and fidelity.

## Relationships

- A reference produces a style fingerprint.
- A semantic specification plus a style fingerprint produces an editable artifact.
- A design family supplies defaults; the fingerprint overrides evidence-backed values.
- Structural verification precedes visual verification.

## Flagged ambiguities

- “Canvas” may mean Canva or a generic raster/design canvas; integrations must name the source explicitly.
- “Same style” may mean template-preserving continuation or looser style transfer; callers must select a mode.
