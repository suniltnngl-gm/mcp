#!/usr/bin/env python3
"""AI Prompt Generator - Create effective prompts for code tasks"""

from typing import Dict, List

class PromptGenerator:
    """Generate structured prompts for AI code tasks"""
    
    PERSONAS = {
        'security': 'You are a security expert specializing in vulnerability detection and secure coding practices.',
        'performance': 'You are a performance optimization expert focused on efficiency and scalability.',
        'architect': 'You are a software architect with expertise in system design and best practices.',
        'reviewer': 'You are an experienced code reviewer focused on quality, maintainability, and standards.',
        'tester': 'You are a testing expert specializing in test coverage and quality assurance.',
    }
    
    def code_review(self, code: str, language: str = 'python', 
                    focus: str = 'general', context: str = '') -> str:
        """Generate prompt for code review"""
        
        persona = self.PERSONAS.get(focus, self.PERSONAS['reviewer'])
        
        prompt = f"""{persona}

Review this {language} code for:
- Bugs and potential issues
- Security vulnerabilities
- Performance concerns
- Code quality and maintainability
- Best practices adherence

{f"Context: {context}" if context else ""}

Code:
```{language}
{code}
```

Provide:
1. Issues found (severity: high/medium/low)
2. Specific recommendations
3. Code examples for fixes
4. Overall assessment

Be concise and actionable."""
        
        return prompt
    
    def generate_code(self, task: str, language: str = 'python',
                     requirements: List[str] = None, context: str = '') -> str:
        """Generate prompt for code generation"""
        
        reqs = '\n'.join(f"- {r}" for r in (requirements or []))
        
        prompt = f"""You are an expert {language} developer.

Task: {task}

Requirements:
{reqs if reqs else "- Follow best practices\n- Include error handling\n- Add docstrings/comments"}

{f"Context: {context}" if context else ""}

Generate:
1. Clean, production-ready code
2. Proper error handling
3. Documentation/comments
4. Example usage

Language: {language}
Output: Complete, working code only."""
        
        return prompt
    
    def generate_tests(self, code: str, language: str = 'python') -> str:
        """Generate prompt for test generation"""
        
        prompt = f"""{self.PERSONAS['tester']}

Generate comprehensive unit tests for this {language} code:

```{language}
{code}
```

Include:
1. Happy path tests
2. Edge cases
3. Error conditions
4. Mock external dependencies
5. Clear test names

Framework: pytest for Python, Jest for JavaScript
Coverage target: 80%+

Output: Complete test file."""
        
        return prompt
    
    def refactor(self, code: str, goal: str, language: str = 'python') -> str:
        """Generate prompt for refactoring"""
        
        prompt = f"""{self.PERSONAS['architect']}

Refactor this {language} code to: {goal}

Current code:
```{language}
{code}
```

Provide:
1. Refactored code
2. Explanation of changes
3. Benefits of refactoring
4. Migration notes (if breaking changes)

Maintain:
- Functionality
- Existing tests compatibility
- Clear documentation"""
        
        return prompt
    
    def explain_code(self, code: str, language: str = 'python',
                    audience: str = 'developer') -> str:
        """Generate prompt for code explanation"""
        
        prompt = f"""Explain this {language} code for a {audience}:

```{language}
{code}
```

Provide:
1. High-level overview
2. Step-by-step breakdown
3. Key concepts used
4. Potential improvements

Style: Clear, concise, {audience}-appropriate."""
        
        return prompt
    
    def debug(self, code: str, error: str, language: str = 'python') -> str:
        """Generate prompt for debugging"""
        
        prompt = f"""You are a debugging expert.

This {language} code produces an error:

Code:
```{language}
{code}
```

Error:
```
{error}
```

Provide:
1. Root cause analysis
2. Fixed code
3. Explanation of the fix
4. Prevention tips

Be specific and actionable."""
        
        return prompt

def main():
    """CLI interface"""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage:")
        print("  prompt_generator.py review <file>")
        print("  prompt_generator.py generate <task>")
        print("  prompt_generator.py test <file>")
        print("  prompt_generator.py refactor <file> <goal>")
        print("  prompt_generator.py explain <file>")
        print("  prompt_generator.py debug <file> <error>")
        sys.exit(1)
    
    gen = PromptGenerator()
    cmd = sys.argv[1]
    
    if cmd == 'review' and len(sys.argv) > 2:
        with open(sys.argv[2]) as f:
            code = f.read()
        print(gen.code_review(code))
    
    elif cmd == 'generate' and len(sys.argv) > 2:
        task = ' '.join(sys.argv[2:])
        print(gen.generate_code(task))
    
    elif cmd == 'test' and len(sys.argv) > 2:
        with open(sys.argv[2]) as f:
            code = f.read()
        print(gen.generate_tests(code))
    
    elif cmd == 'refactor' and len(sys.argv) > 3:
        with open(sys.argv[2]) as f:
            code = f.read()
        goal = ' '.join(sys.argv[3:])
        print(gen.refactor(code, goal))
    
    elif cmd == 'explain' and len(sys.argv) > 2:
        with open(sys.argv[2]) as f:
            code = f.read()
        print(gen.explain_code(code))
    
    elif cmd == 'debug' and len(sys.argv) > 3:
        with open(sys.argv[2]) as f:
            code = f.read()
        error = ' '.join(sys.argv[3:])
        print(gen.debug(code, error))

if __name__ == '__main__':
    main()
