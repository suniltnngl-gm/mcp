# Maintenance Guide - Code Review Toolkit

This guide explains how to maintain and extend the shared code review toolkit.

---

## 📦 Package Structure

```
code-review-toolkit/
├── src/code_review_toolkit/
│   ├── __init__.py           # Package exports
│   ├── cache.py              # Review caching
│   ├── ai_reviewer.py        # AI-powered review
│   ├── custom_rules.py       # Custom rule engine
│   ├── parallel.py           # Parallel processing
│   └── pattern_learner.py    # Pattern learning
├── tests/                    # Test suite
├── examples/                 # Usage examples
├── pyproject.toml           # Package configuration
└── README.md                # User documentation
```

---

## 🔧 Making Changes

### Adding a New Feature

1. **Create the module**
   ```bash
   cd src/code_review_toolkit
   touch new_feature.py
   ```

2. **Implement the feature**
   ```python
   # new_feature.py
   class NewFeature:
       def __init__(self):
           pass
       
       def do_something(self):
           pass
   ```

3. **Add tests**
   ```bash
   cd tests
   touch test_new_feature.py
   ```

4. **Export in __init__.py**
   ```python
   from .new_feature import NewFeature
   ```

5. **Update documentation**
   - Update README.md
   - Add example usage
   - Update version in pyproject.toml

6. **Test in all projects**
   ```bash
   cd Projects/coding-agent && uv run pytest
   cd Projects/unified-devflow && pytest
   ```

### Fixing a Bug

1. **Identify the bug**
   - Check which module is affected
   - Write a failing test

2. **Fix the bug**
   - Make minimal changes
   - Ensure tests pass

3. **Verify in all projects**
   - Test in coding-agent
   - Test in unified-devflow
   - Test in dev-refactor

4. **Document the fix**
   - Update CHANGELOG
   - Bump version if needed

### Updating Dependencies

1. **Update pyproject.toml**
   ```toml
   dependencies = [
       "google-generativeai>=0.4.0",  # Updated
   ]
   ```

2. **Reinstall in all projects**
   ```bash
   cd Projects/coding-agent
   uv pip install -e ../../shared-tools/code-review-toolkit
   ```

3. **Test thoroughly**

---

## 🧪 Testing

### Run All Tests
```bash
cd shared-tools/code-review-toolkit
pytest tests/ -v
```

### Run Specific Test
```bash
pytest tests/test_cache.py -v
```

### Test in Projects
```bash
# coding-agent
cd Projects/coding-agent
uv run pytest tests/

# unified-devflow
cd Projects/unified-devflow
pytest tests/
```

---

## 📝 Documentation

### Update README
When adding features, update:
- Feature list
- Usage examples
- API reference

### Update Examples
Add practical examples in `examples/` directory.

### Update Version
Follow semantic versioning:
- Major: Breaking changes
- Minor: New features
- Patch: Bug fixes

---

## 🚀 Deployment

### To All Projects

1. **Make changes in shared package**
2. **Test locally**
3. **Commit changes**
4. **Projects automatically use new version** (editable install)

### Version Release

1. **Update version in pyproject.toml**
2. **Update CHANGELOG.md**
3. **Tag release**
   ```bash
   git tag v1.1.0
   git push --tags
   ```

---

## 🔍 Troubleshooting

### Import Errors
```bash
# Reinstall package
uv pip install -e /path/to/code-review-toolkit
```

### Test Failures
```bash
# Run with verbose output
pytest tests/ -vv

# Run specific test
pytest tests/test_cache.py::test_cache_basic -vv
```

### Circular Dependencies
- Check import order in __init__.py
- Use lazy imports if needed

---

## 📊 Monitoring

### Usage Tracking
Monitor which features are most used:
- Check logs
- Gather feedback
- Prioritize improvements

### Performance
- Monitor API costs
- Track cache hit rates
- Measure review times

---

## 🎯 Best Practices

1. **Test everything** - No changes without tests
2. **Document changes** - Update docs immediately
3. **Communicate** - Inform team of breaking changes
4. **Version carefully** - Follow semantic versioning
5. **Keep it simple** - Don't over-engineer

---

## 📞 Support

For questions:
1. Check this maintenance guide
2. Review package documentation
3. Check project migration notes
4. Ask the team

---

**Remember**: This package is used by multiple projects. Changes affect everyone!
