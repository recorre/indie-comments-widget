import json
import sys

def generate_markdown_from_openapi(openapi_data):
    lines = []
    info = openapi_data.get("info", {})
    title = info.get("title", "API Documentation")
    version = info.get("version", "N/A")
    description = info.get("description", "")

    lines.append(f"# {title}")
    lines.append(f"**Version:** {version}\n")
    if description:
        lines.append(f"> {description}\n")

    for path, methods in openapi_data.get("paths", {}).items():
        lines.append(f"\n## `{path}`")
        for method, details in methods.items():
            lines.append(f"\n### {method.upper()}")
            lines.append(f"**Summary:** {details.get('summary', '—')}")
            lines.append(f"\n**Description:** {details.get('description', '—')}")

            params = details.get("parameters", [])
            if params:
                lines.append("\n#### Parameters:")
                for p in params:
                    name = p.get("name")
                    required = "✅" if p.get("required") else "❌"
                    schema = p.get("schema", {}).get("type", "")
                    lines.append(f"- **{name}** ({schema}) — required: {required}")

            if "requestBody" in details:
                lines.append("\n#### Request Body:")
                content = details["requestBody"].get("content", {})
                for media_type, schema_info in content.items():
                    schema = schema_info.get("schema", {})
                    props = schema.get("properties", {})
                    lines.append(f"- Content-Type: `{media_type}`")
                    for field, field_info in props.items():
                        req = "✅" if field in schema.get("required", []) else "❌"
                        ftype = field_info.get("type", "object")
                        desc = field_info.get("description", "")
                        lines.append(f"  - **{field}** ({ftype}) — required: {req} — {desc}")

            lines.append("\n#### Responses:")
            for code, resp in details.get("responses", {}).items():
                desc = resp.get("description", "")
                lines.append(f"- **{code}** — {desc}")

    return "\n".join(lines)

def main():
    print("📋 Cole o JSON do OpenAPI abaixo e pressione Ctrl+D (Linux/macOS) ou Ctrl+Z (Windows) para finalizar:\n")
    raw_input = sys.stdin.read().strip()
    if not raw_input:
        print("❌ Nenhum texto colado.")
        return

    try:
        openapi_data = json.loads(raw_input)
    except json.JSONDecodeError:
        print("❌ O texto colado não é um JSON válido.")
        return

    markdown = generate_markdown_from_openapi(openapi_data)
    with open("api_docs.md", "w", encoding="utf-8") as f:
        f.write(markdown)
    print("✅ Arquivo 'api_docs.md' gerado com sucesso!")

if __name__ == "__main__":
    main()

