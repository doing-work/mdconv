# Comprehensive Document Components Test

This document tests various components that may appear in a document.

## 1. Text Formatting

This section tests **bold text**, *italic text*, ***bold and italic***, `inline code`, and ~~strikethrough~~.

### Subsection with Emphasis

- **Bold words** in a sentence
- *Italic words* for emphasis
- `Code snippets` inline
- ~~Deleted text~~ example
- Normal text with **mixed** formatting

## 2. Headings Hierarchy

# Heading Level 1
## Heading Level 2
### Heading Level 3
#### Heading Level 4
##### Heading Level 5
###### Heading Level 6

## 3. Lists

### Unordered Lists

- First item
- Second item
  - Nested item 1
  - Nested item 2
    - Deeply nested item
- Third item

### Ordered Lists

1. First numbered item
2. Second numbered item
   1. Nested numbered item
   2. Another nested item
3. Third numbered item

### Mixed Lists

- Unordered item
  1. Nested ordered item
  2. Another nested ordered item
- Another unordered item

## 4. Tables

### Simple Table

| Column 1 | Column 2 | Column 3 |
|----------|----------|----------|
| Row 1, Col 1 | Row 1, Col 2 | Row 1, Col 3 |
| Row 2, Col 1 | Row 2, Col 2 | Row 2, Col 3 |
| Row 3, Col 1 | Row 3, Col 2 | Row 3, Col 3 |

### Table with Alignment

| Left Aligned | Center Aligned | Right Aligned |
|:-------------|:--------------:|--------------:|
| Left | Center | Right |
| Text | Text | Text |
| More | Content | Here |

### Table with Formatting

| Feature | Status | Notes |
|---------|--------|-------|
| **Bold** | ✅ Working | *Italic* notes |
| `Code` | ⚠️ Partial | Some issues |
| Links | ✅ Working | [Example](https://example.com) |

## 5. Code Blocks

### Inline Code

Use `print("Hello, World!")` in your code.

### Code Block (Python)

```python
def hello_world():
    """A simple function."""
    print("Hello, World!")
    return True

# This is a comment
if __name__ == "__main__":
    hello_world()
```

### Code Block (JavaScript)

```javascript
function greet(name) {
    console.log(`Hello, ${name}!`);
    return `Greetings, ${name}`;
}

greet("World");
```

### Code Block (No Language)

```
This is plain text code block
with multiple lines
and no syntax highlighting
```

## 6. Links

- [Regular link](https://example.com)
- [Link with title](https://example.com "Example Website")
- [Relative link](./other-file.md)
- [Anchor link](#tables)
- **Bold link**: [Example](https://example.com)
- Auto-link: https://example.com
- Email: <user@example.com>

## 7. Images

### Image with Alt Text

![Sample Image](https://via.placeholder.com/300x200 "Placeholder Image")

### Image with Link

[![Linked Image](https://via.placeholder.com/200x100)](https://example.com)

### Local Image Reference

![Local Image](./image.png)

## 8. Blockquotes

> This is a simple blockquote.
> It can span multiple lines.

### Nested Blockquotes

> First level quote
> > Second level quote
> > > Third level quote

### Blockquote with Formatting

> This blockquote contains **bold text**, *italic text*, and `code`.
> 
> It also has multiple paragraphs.
> 
> - And even lists
> - Inside blockquotes

## 9. Horizontal Rules

---

Above and below horizontal rule

---

## 10. Math Expressions (if supported)

Inline math: $E = mc^2$

Block math:

$$
\int_{-\infty}^{\infty} e^{-x^2} dx = \sqrt{\pi}
$$

## 11. Task Lists

- [x] Completed task
- [x] Another completed task
- [ ] Incomplete task
- [ ] Another incomplete task

## 12. Definition Lists

Term 1
: Definition 1

Term 2
: Definition 2a
: Definition 2b

## 13. Escaped Characters

\*Not italic\* \`Not code\` \#Not heading

## 14. Special Characters

- Copyright: ©
- Trademark: ™
- Registered: ®
- Em dash: —
- En dash: –
- Ellipsis: …
- Quotes: "smart quotes" and 'single quotes'

## 15. Mixed Content

This paragraph contains **bold**, *italic*, `code`, and a [link](https://example.com).

> Blockquote with **formatting** and `code`
> 
> - List item 1
> - List item 2

| Table | With | Formatting |
|-------|------|------------|
| **Bold** | *Italic* | `Code` |

```python
# Code block
print("Hello")
```

---

End of test document.

