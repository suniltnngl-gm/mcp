#!/bin/bash

# Document Consolidation System - Aggressive Mode
# Target: 43 → 12 files (72% reduction)

# Source context protection
source ./context-protection.sh 2>/dev/null || {
    # Fallback protected files if context-protection.sh not available
    CONTEXT_FILES=(
        "AmazonQ.md"
        "AGENTS.md" 
        "README.md"
        ".amazonq/rules/default.md"
    )
}



# Aggressive consolidation rules
declare -A AGGRESSIVE_RULES=(
    # Core documentation (4 files)
    ["README.md"]="README.md"
    ["CHANGELOG.md,NEXT_STEPS.md,IMPROVEMENT_PROPOSALS.md"]="WORKFLOW.md"
    ["docs/AI_MODELS.md,docs/PERFORMANCE.md,MODEL_VERSIONS.md,OPENAI_COMPATIBILITY.md,AI_TROUBLESHOOTING.md"]="AI_GUIDE.md"
    ["docs/ARCHITECTURE.md,docs/API_DOCS.md,docs/ROADMAP.md,docs/INTEGRATIONS.md"]="TECHNICAL_DOCS.md"
    
    # Development documentation (3 files)
    ["docs/CONTRIBUTING.md,docs/TESTING.md,docs/TOOLS.md"]="DEVELOPMENT.md"
    ["docs/SECURITY.md,SECURITY_SETUP.md,docs/DEPLOYMENT.md"]="SECURITY_DEPLOYMENT.md"
    ["docs/TROUBLESHOOTING.md,WARP.md"]="TROUBLESHOOTING.md"
    
    # Project management (2 files)
    ["WORKFLOW_COMPLIANCE_ANALYSIS.md,PROJECT_ASSESSMENT.md,DOCUMENTATION_REVIEW_SUMMARY.md"]="PROJECT_STATUS.md"
    ["proposals/*.md"]="PROPOSALS.md"
    
    # Knowledge & case studies (3 files)
    ["knowledge-base/**/*.md"]="KNOWLEDGE_BASE.md"
    ["case-studies/**/*.md"]="CASE_STUDIES.md"
    [".github/**/*.md"]="GITHUB_TEMPLATES.md"
)

aggressive_consolidate() {
    echo "🎯 AGGRESSIVE CONSOLIDATION: Excluding protected context files"
    
    # Build exclude pattern for protected files
    EXCLUDE_PATTERN=""
    for file in "${CONTEXT_FILES[@]}"; do
        EXCLUDE_PATTERN="$EXCLUDE_PATTERN -not -name \"$file\""
    done
    
    # Create backup (excluding protected files from analysis)
    mkdir -p .backup/docs-$(date +%Y%m%d-%H%M)
    find . -name "*.md" -not -path "./node_modules/*" \
        -not -name "WORKFLOW.md" \
        -not -name "GEMINI.md" \
        -not -name "AmazonQ.md" \
        -not -name "AGENTS.md" \
        -not -name "README.md" \
        -not -path "./.amazonq/*" \
        -exec cp {} .backup/docs-$(date +%Y%m%d-%H%M)/ \; 2>/dev/null
    
    # Create consolidated files (protected files not included in consolidation)
    # Note: WORKFLOW.md is protected and will not be updated
    
    echo "# AI Integration Guide" > AI_GUIDE.md  
    [ -f docs/AI_MODELS.md ] && cat docs/AI_MODELS.md >> AI_GUIDE.md 2>/dev/null
    [ -f docs/PERFORMANCE.md ] && cat docs/PERFORMANCE.md >> AI_GUIDE.md 2>/dev/null
    [ -f MODEL_VERSIONS.md ] && cat MODEL_VERSIONS.md >> AI_GUIDE.md 2>/dev/null
    [ -f OPENAI_COMPATIBILITY.md ] && cat OPENAI_COMPATIBILITY.md >> AI_GUIDE.md 2>/dev/null
    [ -f AI_TROUBLESHOOTING.md ] && cat AI_TROUBLESHOOTING.md >> AI_GUIDE.md 2>/dev/null
    
    echo "# Technical Documentation" > TECHNICAL_DOCS.md
    [ -f docs/ARCHITECTURE.md ] && cat docs/ARCHITECTURE.md >> TECHNICAL_DOCS.md 2>/dev/null
    [ -f docs/API_DOCS.md ] && cat docs/API_DOCS.md >> TECHNICAL_DOCS.md 2>/dev/null
    [ -f docs/ROADMAP.md ] && cat docs/ROADMAP.md >> TECHNICAL_DOCS.md 2>/dev/null
    [ -f docs/INTEGRATIONS.md ] && cat docs/INTEGRATIONS.md >> TECHNICAL_DOCS.md 2>/dev/null
    
    echo "# Development Guide" > DEVELOPMENT.md
    [ -f docs/CONTRIBUTING.md ] && cat docs/CONTRIBUTING.md >> DEVELOPMENT.md 2>/dev/null
    [ -f docs/TESTING.md ] && cat docs/TESTING.md >> DEVELOPMENT.md 2>/dev/null
    [ -f docs/TOOLS.md ] && cat docs/TOOLS.md >> DEVELOPMENT.md 2>/dev/null
    
    echo "# Security & Deployment" > SECURITY_DEPLOYMENT.md
    [ -f docs/SECURITY.md ] && cat docs/SECURITY.md >> SECURITY_DEPLOYMENT.md 2>/dev/null
    [ -f SECURITY_SETUP.md ] && cat SECURITY_SETUP.md >> SECURITY_DEPLOYMENT.md 2>/dev/null
    [ -f docs/DEPLOYMENT.md ] && cat docs/DEPLOYMENT.md >> SECURITY_DEPLOYMENT.md 2>/dev/null
    
    echo "# Troubleshooting" > TROUBLESHOOTING_GUIDE.md
    [ -f docs/TROUBLESHOOTING.md ] && cat docs/TROUBLESHOOTING.md >> TROUBLESHOOTING_GUIDE.md 2>/dev/null
    [ -f WARP.md ] && cat WARP.md >> TROUBLESHOOTING_GUIDE.md 2>/dev/null
    
    echo "# Project Status" > PROJECT_STATUS.md
    [ -f WORKFLOW_COMPLIANCE_ANALYSIS.md ] && cat WORKFLOW_COMPLIANCE_ANALYSIS.md >> PROJECT_STATUS.md 2>/dev/null
    [ -f PROJECT_ASSESSMENT.md ] && cat PROJECT_ASSESSMENT.md >> PROJECT_STATUS.md 2>/dev/null
    [ -f DOCUMENTATION_REVIEW_SUMMARY.md ] && cat DOCUMENTATION_REVIEW_SUMMARY.md >> PROJECT_STATUS.md 2>/dev/null
    
    echo "# Proposals" > PROPOSALS.md
    find ./proposals -name "*.md" -exec cat {} \; >> PROPOSALS.md 2>/dev/null
    
    echo "# Knowledge Base" > KNOWLEDGE_BASE.md
    find ./knowledge-base -name "*.md" -exec cat {} \; >> KNOWLEDGE_BASE.md 2>/dev/null
    
    echo "# Case Studies" > CASE_STUDIES.md
    find ./case-studies -name "*.md" -exec cat {} \; >> CASE_STUDIES.md 2>/dev/null
    
    echo "# GitHub Templates" > GITHUB_TEMPLATES.md
    find ./.github -name "*.md" -exec cat {} \; >> GITHUB_TEMPLATES.md 2>/dev/null
    
    # Remove original files (keep protected files and consolidated files)
    find . -name "*.md" -not -path "./node_modules/*" \
        -not -name "README.md" \
        -not -name "WORKFLOW.md" \
        -not -name "GEMINI.md" \
        -not -name "AmazonQ.md" \
        -not -name "AGENTS.md" \
        -not -path "./.amazonq/*" \
        -not -name "AI_GUIDE.md" \
        -not -name "TECHNICAL_DOCS.md" \
        -not -name "DEVELOPMENT.md" \
        -not -name "SECURITY_DEPLOYMENT.md" \
        -not -name "TROUBLESHOOTING_GUIDE.md" \
        -not -name "PROJECT_STATUS.md" \
        -not -name "PROPOSALS.md" \
        -not -name "KNOWLEDGE_BASE.md" \
        -not -name "CASE_STUDIES.md" \
        -not -name "GITHUB_TEMPLATES.md" \
        -delete 2>/dev/null
    
    # Remove empty directories
    find . -type d -empty -delete 2>/dev/null || true
    
    echo "✅ Consolidation complete. New count: $(find . -name "*.md" -not -path "./node_modules/*" -not -path "./.backup/*" | wc -l)"
    echo "📁 Backup created in: .backup/docs-$(date +%Y%m%d-%H%M)/"
    echo "🔒 Protected context files: ${CONTEXT_FILES[*]} (excluded from consolidation)"
}

case "${1:-help}" in
    aggressive)
        aggressive_consolidate
        ;;
    validate)
        echo "✅ Document consolidation validation:"
        echo "   Current count: $(find . -name "*.md" -not -path "./node_modules/*" -not -path "./.backup/*" | wc -l)"
        echo "   Target: 12 files"
        if [ "$(find . -name "*.md" -not -path "./node_modules/*" -not -path "./.backup/*" | wc -l)" -eq 12 ]; then
            echo "   Status: ✅ TARGET ACHIEVED"
        else
            echo "   Status: ⚠️  Further consolidation needed"
        fi
        ;;
    *)
        echo "Usage: $0 {aggressive|validate}"
        ;;
esac
