# dkdc.dev Website Architecture

This document describes the structure and organization of the dkdc.dev website built with Zola static site generator.

## Overview

The website is built using:
- **Zola** - A fast static site generator written in Rust
- **Terminimal theme** - A minimal, terminal-style theme for Zola
- **Static hosting** - Deployed as static files

## Directory Structure

```
websites/dkdc.dev/
├── config.toml                 # Main Zola configuration
├── content/                    # All content files
│   ├── _index.md              # Homepage content
│   ├── blog/                  # Blog posts directory
│   │   ├── _index.md          # Blog listing page configuration
│   │   ├── post-name.md       # Individual blog posts
│   │   └── post-name/         # Blog posts with assets
│   │       ├── index.md       # Post content
│   │       └── images...      # Post-specific images
│   └── pages/                 # Static pages
│       ├── _index.md          # Pages section config (render=false)
│       ├── about.md           # About page
│       ├── cats.md            # Cats page
│       └── dogs.md            # Dogs page
├── static/                     # Static assets
│   ├── favicon.png            # Site favicon
│   └── img/                   # Shared images
│       ├── cats/              # Cat images
│       └── dogs/              # Dog images
├── templates/                  # Custom template overrides
│   └── shortcodes/            # Custom shortcodes
│       ├── details.html       # Collapsible details
│       └── video.html         # Video embeds
├── themes/                     # Theme directory
│   └── terminimal/            # Terminimal theme
│       ├── templates/         # Theme templates
│       ├── static/            # Theme static assets
│       └── sass/              # Theme styles
└── public/                     # Generated output (git-ignored)
```

## Key Configuration

### config.toml
- Base URL: `https://dkdc.dev`
- Theme: `terminimal`
- Color scheme: Pink accent with dark background
- Custom footer: Minimal "dkdc.dev" link
- Menu structure: blog, about, dogs, cats

### Content Organization

#### Homepage (`content/_index.md`)
- Simple welcome message with links to blog and about

#### Blog (`content/blog/`)
- Posts sorted by date
- Pagination enabled (10 posts per page)
- Posts can have:
  - Frontmatter: title, date, author, tags, draft
  - Summary markers: `<!-- more -->` for post previews
  - Assets: Images/videos in post subdirectories

#### Pages (`content/pages/`)
- Static pages with custom paths
- Not rendered as a section (`render = false`)
- Each page defines its own URL path

### Image Handling

Images are referenced using absolute paths:
- Shared images: `/img/category/image.png`
- Post-specific images: `/blog/post-name/image.png`

### Shortcodes

Custom shortcodes extend functionality:
- `{% details %}` - Collapsible content sections
- `{{ figure() }}` - Images with captions (theme-provided)
- `{{ video() }}` - Video embeds

## Build Process

```bash
# Development server
zola serve

# Production build
zola build

# Output goes to public/ directory
```

## Theme Customization

The Terminimal theme is customized via:
- `config.toml` settings for colors, menus, footer
- Template overrides in `templates/`
- Additional shortcodes in `templates/shortcodes/`

## Migration Notes

This site was migrated from Hugo to Zola:
- Hugo shortcodes converted to Zola syntax
- Image paths updated to absolute URLs
- Blog structure reorganized
- Theme-specific features adapted