#!/bin/bash

# Generate AI insights on project organization
# Minimal implementation using existing AI integration

source ./ai-config.js 2>/dev/null || true
source ./context-protection.sh 2>/dev/null || {
    # Fallback protected files
    CONTEXT_FILES=(
        "AmazonQ.md"
        "AGENTS.md" 
        "README.md"
        ".amazonq/rules/default.md"
    )
}

KB_DIR="knowledge-base/ai-insights"
DATE=$(date +%Y-%m-%d)
INSIGHTS_FILE="$KB_DIR/project-insights-$DATE.json"

# Generate project organization insights
generate_insights() {
    mkdir -p "$KB_DIR"
    
    # Count files by type (using unified ignore patterns)
    source ./unified-ignore-patterns.sh 2>/dev/null || {
        # Fallback to basic counting
        local shell_count=$(find . -name "*.sh" -not -path "./node_modules/*" -not -path "./.git/*" | wc -l)
        local js_count=$(find . -name "*.js" -not -path "./node_modules/*" -not -path "./.git/*" | wc -l)
        local md_count=$(find . -name "*.md" -not -path "./node_modules/*" -not -path "./.git/*" \
            -not -name "AmazonQ.md" -not -name "AGENTS.md" -not -name "README.md" -not -path "./.amazonq/*" | wc -l)
    }
    
    # Use unified patterns if available
    if command -v build_dir_excludes >/dev/null 2>&1; then
        local dir_excludes=$(build_dir_excludes)
        local file_excludes=$(build_file_excludes)
        local shell_count=$(eval "find . -name '*.sh' $dir_excludes $file_excludes" | wc -l)
        local js_count=$(eval "find . -name '*.js' $dir_excludes $file_excludes" | wc -l)
        local md_count=$(find . -name "*.md" -not -path "./node_modules/*" -not -path "./.git/*" \
            -not -name "AmazonQ.md" -not -name "AGENTS.md" -not -name "README.md" -not -path "./.amazonq/*" | wc -l)
    fi
    
    # Generate insights JSON
    cat > "$INSIGHTS_FILE" << EOF
{
  "generated": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "project_structure": {
    "shell_scripts": $shell_count,
    "javascript_files": $js_count,
    "markdown_docs": $md_count,
    "total_files": $((shell_count + js_count + md_count))
  },
  "architecture_patterns": [
    "Unified entry point (main.sh)",
    "Workflow automation system",
    "AI integration layer",
    "Knowledge base structure"
  ],
  "key_components": [
    "task-manager.sh - Task lifecycle management",
    "workflow-parser.sh - Standardized parsing",
    "knowledge-base-ai.sh - AI integration",
    "main.sh - Unified interface"
  ],
  "recommendations": [
    "Continue using standardized workflow parsing",
    "Maintain unified entry point pattern",
    "Expand knowledge base with more patterns",
    "Keep minimal implementations"
  ]
}
EOF
    
    echo "✅ AI insights generated: $INSIGHTS_FILE"
}

main() {
    echo "🧠 Generating AI insights on project organization..."
    generate_insights
}

main "$@"
