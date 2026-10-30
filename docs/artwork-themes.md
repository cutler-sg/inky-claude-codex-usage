# Artwork themes — agreed direction

The user has retained the six Street Fighter concepts as a second theme and
requested a Marvel-versus-DC concept set next. This is the control scheme for
future implementation; theme switching is **deferred and not deployed**. The current D button
still selects Budget Kraken.

| Control | Planned behaviour |
| --- | --- |
| A | Previous artwork within the selected theme; lock that artwork. |
| B | Next artwork within the selected theme; lock that artwork. |
| C | Random artwork within the selected theme; resume automatic rotation. |
| D | Switch to the next theme, replacing the Budget Kraken shortcut. |
| Automatic refresh | Rotate only among artwork in the selected theme. |

Theme selection should persist across refreshes and service restarts. Selecting
an artwork, refreshing usage or pressing random must not switch themes. A simple
proposed default for D is to select the first artwork in the next theme and resume
rotation; the implementation should make this behaviour explicit.

## Sets

- **Original:** the six live compositions, from Pop Comic to Cosmic Pinball.
- **Street Fighter:** the [retained arcade mockups](../designs/arcade-pack/README.md).
- **Marvel versus DC:** the [new crossover mockups](../designs/marvel-dc-pack/README.md),
  under design review.

The new sets are concept images with fixed example readings. Before they become
selectable on the Pi, they need clean plates, real usage overlays, full data-state
handling and display-profile/palette validation. Fixed mockup readings must not
be shown as live usage. The user explicitly chose to finish the Marvel/DC mockups
first and revisit full theme switching separately at a later date.
