---
name: Amber Essence Smart Home
colors:
  surface: '#fef9f1'
  surface-dim: '#ded9d2'
  surface-bright: '#fef9f1'
  surface-container-lowest: '#ffffff'
  surface-container-low: '#f8f3eb'
  surface-container: '#f2ede5'
  surface-container-high: '#ece8e0'
  surface-container-highest: '#e7e2da'
  on-surface: '#1d1c17'
  on-surface-variant: '#554336'
  inverse-surface: '#32302b'
  inverse-on-surface: '#f5f0e8'
  outline: '#887364'
  outline-variant: '#dbc2b0'
  surface-tint: '#904d00'
  primary: '#8d4b00'
  on-primary: '#ffffff'
  primary-container: '#b15f00'
  on-primary-container: '#fffbff'
  inverse-primary: '#ffb77d'
  secondary: '#795900'
  on-secondary: '#ffffff'
  secondary-container: '#ffc329'
  on-secondary-container: '#6f5100'
  tertiary: '#006096'
  on-tertiary: '#ffffff'
  tertiary-container: '#007abd'
  on-tertiary-container: '#fdfcff'
  error: '#ba1a1a'
  on-error: '#ffffff'
  error-container: '#ffdad6'
  on-error-container: '#93000a'
  primary-fixed: '#ffdcc3'
  primary-fixed-dim: '#ffb77d'
  on-primary-fixed: '#2f1500'
  on-primary-fixed-variant: '#6e3900'
  secondary-fixed: '#ffdf9f'
  secondary-fixed-dim: '#f9bd22'
  on-secondary-fixed: '#261a00'
  on-secondary-fixed-variant: '#5c4300'
  tertiary-fixed: '#cee5ff'
  tertiary-fixed-dim: '#96ccff'
  on-tertiary-fixed: '#001d32'
  on-tertiary-fixed-variant: '#004a75'
  background: '#fef9f1'
  on-background: '#1d1c17'
  surface-variant: '#e7e2da'
  shadow-dark: '#e5dfd3'
  shadow-light: '#ffffff'
  status-green: '#16a34a'
  status-red: '#dc2626'
  glass-bg: rgba(253, 248, 240, 0.7)
typography:
  headline-lg:
    fontFamily: Plus Jakarta Sans
    fontSize: 24px
    fontWeight: '700'
    lineHeight: 32px
  headline-md:
    fontFamily: Plus Jakarta Sans
    fontSize: 20px
    fontWeight: '600'
    lineHeight: 28px
  body-lg:
    fontFamily: Plus Jakarta Sans
    fontSize: 16px
    fontWeight: '500'
    lineHeight: 24px
  body-sm:
    fontFamily: Plus Jakarta Sans
    fontSize: 14px
    fontWeight: '400'
    lineHeight: 20px
  data-display:
    fontFamily: JetBrains Mono
    fontSize: 28px
    fontWeight: '600'
    lineHeight: 32px
    letterSpacing: -1px
  data-label:
    fontFamily: JetBrains Mono
    fontSize: 12px
    fontWeight: '500'
    lineHeight: 16px
    letterSpacing: 1px
  label-caps:
    fontFamily: Plus Jakarta Sans
    fontSize: 11px
    fontWeight: '700'
    lineHeight: 16px
    letterSpacing: 0.5px
rounded:
  sm: 0.25rem
  DEFAULT: 0.5rem
  md: 0.75rem
  lg: 1rem
  xl: 1.5rem
  full: 9999px
spacing:
  container-padding: 1.5rem
  card-gap: 1rem
  section-margin: 2rem
  element-padding: 1rem
  max-width: 480px
---

## Brand & Style

This design system embodies a warm, tactile, and highly accessible smart home experience. It targets users who appreciate technology that feels "physical" rather than purely digital, evoking a sense of comfort and domestic energy.

The aesthetic is a sophisticated blend of **Neomorphism** and **Glassmorphism**. 
- **Neomorphism** is used for the primary interface structure, utilizing soft, double-shadowed "extruded" surfaces that mimic physical plastic or soft-touch materials.
- **Glassmorphism** is reserved for high-level navigation and overlays to provide a sense of modern airiness and spatial layering.
- The overall mood is **warm, inviting, and technical yet soft**, reducing the coldness often associated with IoT dashboards.

## Colors

The palette is centered around the **Sunset Amber** theme. The primary color is a rich, energetic amber that draws attention to active states and primary actions.

- **Primary Amber (#d97706):** Used for active icons, primary toggles, and critical status highlights.
- **Surface (Background):** The off-white `#fdf8f0` acts as the base material for all neumorphic elements.
- **Neumorphic Shadows:** Use `#e5dfd3` for the "dark" bottom-right shadow and `#ffffff` for the "light" top-left highlight to create the 3D extrusion effect.
- **Glass Elements:** Use the `glass-bg` with a heavy backdrop blur for the navigation bar to differentiate it from the tactile cards below.

## Typography

The typography system creates a clear distinction between UI guidance and sensor data.

- **UI Language:** `Plus Jakarta Sans` provides a friendly, contemporary feel for headings, buttons, and descriptions. Its rounded terminals complement the soft neumorphic shapes.
- **Sensor & Technical Data:** `JetBrains Mono` is used exclusively for numerical sensor values (temperature, humidity, light levels) and the communication log. This monospaced font conveys precision and a "maker" aesthetic suitable for an ESP32-based project.
- **Hierarchical Scale:** Headlines use bold weights to anchor the cards, while labels use all-caps for technical metadata.

## Layout & Spacing

The layout is designed as a **fixed-width mobile-first dashboard** with a maximum width of 480px, optimized for smartphone screens or centered viewing on tablets/desktops.

- **The Grid:** A 2-column responsive grid is used for sensor cards, while control buttons may span full width or 2-columns depending on importance.
- **Rhythm:** A consistent 1rem (16px) gap exists between all neumorphic cards to ensure shadows do not overlap messily.
- **Safe Areas:** Generous top and bottom margins (2rem) ensure the UI feels balanced, particularly when the glassmorphic bottom navigation is present.

## Elevation & Depth

Hierarchy is achieved through two distinct methods:

1.  **Neumorphic Extrusion (Tactile):** 
    - **Raised (Default):** Cards and inactive buttons use a `6px 6px 12px` dark shadow and a `-6px -6px 12px` light highlight.
    - **Sunken (Active/Pressed):** Active states, input fields, and the terminal log use `inset` shadows to appear "pressed" into the surface.
2.  **Glassmorphic Layering (Spatial):** 
    - The bottom navigation and connection overlays use `backdrop-filter: blur(12px)` and a subtle `1px` semi-transparent border. This places them on a higher spatial plane than the tactile dashboard controls.

## Shapes

The design uses a **Rounded (Level 2)** shape language.
- **Cards:** 1rem (16px) corner radius for a friendly, modern feel.
- **Buttons:** 1rem corner radius, or full pill-shape for small chips/badges.
- **Circular Monitors:** Sensor gauges for temperature and humidity should be perfect circles to contrast with the rectangular grid of the dashboard.

## Components

### Neumorphic Cards
The primary container for sensor data. These feature a "raised" surface. Inside, sensor values are displayed in `JetBrains Mono`.

### Circular Sensor Monitors
Circular gauges for temperature/humidity. The progress ring should be the Primary Amber color, with the center of the circle appearing "sunken" (inset shadow) or "raised" depending on the visual density required.

### Control Buttons
- **Default State:** Raised neumorphic rectangle.
- **Active State:** Sunken neumorphic rectangle with the icon or text changing to Primary Amber.
- **Iconography:** Use thick-stroke (2px) rounded icons that match the weight of Plus Jakarta Sans.

### Status Badges
Small pill-shaped elements for BLE connection status.
- **Connected:** Green background with white text.
- **Scanning:** Amber pulse animation.
- **Disconnected:** Sunken neutral state.

### Glass Navigation Bar
A fixed bottom bar using glassmorphism. Icons should be centered with high-contrast active states.

### Communication Terminal
A large, full-width "sunken" panel at the bottom of the dashboard using `JetBrains Mono` for raw TX/RX logs, styled to look like a screen recessed into the device's body.