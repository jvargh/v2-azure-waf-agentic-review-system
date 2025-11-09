# Converting Word Docs to Markdown

The script `scripts/convert_docx_to_md.py` converts `.docx` documents into Markdown for easier version control and diffing.

## Usage

1. Place the `.docx` file in an accessible path (adjust the path in the script if needed).
2. Run the script:
   
   ```bash
   pwsh.exe -NoLogo -File scripts/convert_docx_to_md.py
   ```

3. The script will:
   - Install `python-docx` if missing.
   - Generate a `.md` file adjacent to the source document.
   - Print a preview of the first ~1000 characters.

## Features

- Detects heading styles (Heading 1..6) and maps them to `#` prefixes.
- Converts list-styled paragraphs to Markdown bullet points.
- Extracts tables and converts them to Markdown table syntax.
- Preserves blank lines to keep paragraph separation.

## Adjusting Source Path

Edit the `docx_file` variable near the bottom of the script to point to your Word document:

```python
docx_file = Path("src/docs/Detailed User Flow.docx")
```

## Troubleshooting

| Issue | Cause | Fix |
|-------|-------|-----|
| `Import "docx" could not be resolved` | `python-docx` not installed in current environment | The script auto-installs; rerun or manually `pip install python-docx` |
| Output file empty | Document paragraphs styles not standard | Open docx and ensure content isn't inside text boxes or unusual containers |
| Missing images | Script doesn't handle embedded images | Export images manually and embed via Markdown `![]()` syntax |

## Future Enhancements

- Image extraction
- Inline bold/italic formatting
- Hyperlink conversion
- Support for numbered lists

## Related

See `docs/AGENT_REPLICATION_BLUEPRINT.md` and other markdown docs for structure conventions.
