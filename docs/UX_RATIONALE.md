# TerraFly UI/UX rationale

This document lets any team member explain the interface instead of saying that an AI chose it.

## References reviewed

- The four Day 1 screenshots captured after running `tir_100m_512.png`.
- Kole Jain, [“5 SaaS UI/UX mistakes that SCREAM you Vibe Code”](https://www.youtube.com/watch?v=PDcQJOPby1k), reviewed 2026-08-25. We used its general design lessons, not its sponsor or a copied layout: remove decorative emoji-like elements, control the palette, avoid repeated KPIs/cards, remove controls that do nothing, prioritize useful information, and design around the product's main task.
- The three SAC IR-colorization preview PNGs supplied by the team. Their scientific role is documented in `DATA_SOURCES.md`.

## What the first interface did well

- It made the `Relative` scientific state visible.
- It showed real job progress instead of a fake animation.
- It placed the input and predicted surface side by side.
- It exposed provenance, artifact downloads, and display-only vertical exaggeration.
- It gave the 3D viewer enough room to demonstrate the core idea.

Those behaviors were preserved.

## What made it look generated

1. A dark-green gradient, bright mint accent, glowing status dot, shaped `TF` badge, numbered cards, pills, and many rounded containers all competed for attention.
2. `Relative` appeared in the header, promise banner, result card, units pill, and warning copy. Repeating the same fact weakened the hierarchy.
3. Five circular progress markers duplicated the progress bar.
4. Disabled `Metric GeoTIFF` and `GLB mesh` rows advertised features that did not work. A professional product does not make its roadmap look clickable.
5. The result page treated previews, the 3D viewer, metadata, exports, and warnings as equally important cards. The core product—the explorable surface—did not dominate the layout.
6. Technical fields such as SHA-256 and `.npy` were shown without explaining why a judge or engineer should care.
7. The upload control said files could be dropped, but it did not implement a drop handler.
8. A grayscale thermal preview could run without an explicit out-of-domain warning.

## The revised design system

- **Hierarchy:** the 3D surface is the dominant result; comparison images and provenance form a smaller inspector.
- **Palette:** neutral canvas, white working surfaces, dark viewer, and one restrained teal accent. Amber is reserved for a real scientific caution.
- **Typography:** system UI font for clarity and a monospace font only for identifiers, hashes, and technical labels.
- **Shape:** 6–12 px radii, thin borders, no gradients, no glow, no decorative badges, and no meaningless icons.
- **Layout:** one input workbench, one result workspace, and one evidence list. Information is grouped by task rather than turned into many equal cards.
- **Disclosure:** provenance and method details stay available but are collapsed until someone needs them.
- **Functionality:** only completed exports are interactive. Future metric output is explained as a sentence, not a disabled button.

## Interaction decisions

- Selecting and dropping a file are both real interactions.
- The progress bar and stage labels come from backend state.
- The selected image is previewed before running.
- Single-band inputs receive a visible domain warning.
- Photo/Height colours, numeric legend, sun direction, wireframe, optional Structures, navigation, display exaggeration, point clearing, and reset are kept because each has a current inspection use.
- The viewer shows loading and error states instead of silently rendering an empty box.
- Every downloadable output includes a one-sentence purpose.

## Figma handoff exercise for the UI teammate

Recreate these five frames before changing the code:

1. Empty input state at 1440 px width.
2. Selected-file state.
3. Running state at approximately 50%.
4. Completed RGB result.
5. Completed single-band/TIR demonstration with the domain warning.

Use the tokens in `frontend/src/styles.css` as the current source of truth. In review, the teammate must be able to answer:

- What is the primary action on this screen?
- What is the most important result?
- Why is amber used only for warnings?
- Why is provenance collapsed?
- Why are unavailable exports absent?
- What changes at 980 px and 680 px breakpoints?

Figma is a design and communication tool here; the checked-in React/CSS and browser tests remain the implementation source of truth.
