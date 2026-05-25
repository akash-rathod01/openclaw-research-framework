# Contributing to OpenClaw Research Framework

First off, **thank you** for considering contributing to OpenClaw! 🎉

OpenClaw is an open-source project created by **Akash Rathod** and maintained by the community. We welcome contributions from everyone.

---

## 📜 Code of Conduct

This project follows the standard open-source code of conduct:
- **Be respectful** - Treat all contributors with respect
- **Be constructive** - Provide helpful feedback
- **Be collaborative** - Work together towards improvement
- **Give credit** - Acknowledge others' contributions

---

## 🚀 How to Contribute

### 1. Types of Contributions We Welcome

#### 🐛 Bug Reports
- Found a bug? [Open an issue](https://github.com/akash-rathod01/openclaw-research-framework/issues)
- Include steps to reproduce
- Share your environment (Python version, OS, etc.)
- Paste error messages/logs

#### 💡 Feature Requests
- Have an idea? [Create a feature request](https://github.com/akash-rathod01/openclaw-research-framework/issues)
- Explain the use case
- Describe expected behavior
- Provide examples if possible

#### 📝 Documentation
- Fix typos or improve clarity
- Add tutorials or examples
- Translate to other languages
- Create video walkthroughs

#### 💻 Code Contributions
- New agent skills
- Performance improvements
- Bug fixes
- New features (API, UI, etc.)

---

## 🛠️ Development Setup

### Prerequisites
- Python 3.8+ (3.13 recommended)
- Git
- Virtual environment (recommended)

### Setup Steps

```bash
# 1. Fork the repository on GitHub
# 2. Clone your fork
git clone https://github.com/YOUR-USERNAME/openclaw-research-framework.git
cd openclaw-research-framework

# 3. Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 4. Install dependencies
cd agentic_rnd_tool
pip install -r requirements.txt

# 5. Run tests
python orchestrator.py "https://example.com" --max-sources 5

# 6. Create a feature branch
git checkout -b feature/your-feature-name
```

---

## 📦 Pull Request Process

### Before Submitting

- [ ] Test your changes locally
- [ ] Update documentation if needed
- [ ] Add comments to complex code
- [ ] Follow existing code style
- [ ] Ensure no breaking changes (or document them)

### Submitting

1. **Commit your changes**
   ```bash
   git add .
   git commit -m "Add: Brief description of your changes"
   ```

2. **Push to your fork**
   ```bash
   git push origin feature/your-feature-name
   ```

3. **Open a Pull Request**
   - Go to the original repository
   - Click "New Pull Request"
   - Select your fork and branch
   - Fill out the PR template:
     - **What:** What does this PR do?
     - **Why:** Why is this change needed?
     - **How:** How did you implement it?
     - **Testing:** How did you test it?

4. **Wait for review**
   - Akash Rathod will review your PR
   - Address any feedback
   - Once approved, it will be merged!

---

## 🎨 Code Style Guidelines

### Python Style
- Follow [PEP 8](https://pep8.org/)
- Use 4 spaces for indentation
- Maximum line length: 100 characters
- Use descriptive variable names

### Documentation Style
- Use Markdown for .md files
- Include code examples where helpful
- Keep language clear and concise

### Commit Messages
```
Type: Brief description (50 chars or less)

More detailed explanation if needed (wrap at 72 chars).
Explain WHAT changed and WHY, not HOW.

Examples:
- Add: New security scan feature
- Fix: Resolve JavaScript rendering bug on Firefox
- Docs: Update installation guide for Windows
- Refactor: Improve orchestrator performance
```

---

## 🧪 Testing Guidelines

### Manual Testing
1. Run on at least 3 different websites
2. Test with and without `--javascript` flag
3. Verify reports are generated correctly
4. Check console output for errors

### Test Cases to Cover
- Static HTML sites
- JavaScript-heavy sites (React, Vue)
- Large sites (50+ pages)
- Sites with special characters/Unicode
- Error handling (404s, timeouts)

---

## 📋 Feature Request Template

When proposing a new feature:

```markdown
## Feature Description
Brief description of the feature

## Use Case
Why is this feature needed? Who will use it?

## Proposed Implementation
How would you implement this? (High-level)

## Alternatives Considered
Other ways to solve this problem?

## Additional Context
Screenshots, examples, references?
```

---

## 🐛 Bug Report Template

```markdown
## Bug Description
Clear description of the bug

## Steps to Reproduce
1. Run command: `python orchestrator.py ...`
2. Expected behavior: ...
3. Actual behavior: ...

## Environment
- OS: Windows 11 / macOS / Linux
- Python version: 3.13
- OpenClaw version: 1.0.0

## Error Messages
Paste error logs here

## Screenshots (if applicable)
Add screenshots to help explain
```

---

## 🏆 Recognition & Credits

### How to Get Credit

All contributors will be recognized in:
1. **CONTRIBUTORS.md** - Your name and GitHub link
2. **Release Notes** - Thank you in version releases
3. **README.md** - Major contributors get special mention

### Contribution Tiers

**🥇 Major Contributor** (100+ lines or major feature)
- Full name and bio in CONTRIBUTORS.md
- Co-author credit for that feature
- Special thank you in LinkedIn/social media posts

**🥈 Regular Contributor** (10-99 lines or multiple PRs)
- Name and link in CONTRIBUTORS.md
- Thank you in release notes

**🥉 Community Contributor** (bug reports, testing, feedback)
- Name in release notes
- GitHub contribution graph credit

---

## 🤝 Community Guidelines

### Communication Channels
- **GitHub Issues** - Bug reports, feature requests
- **GitHub Discussions** - General questions, ideas
- **LinkedIn** - Follow Akash Rathod for updates
- **Email** - For private inquiries: akash.rathod01@example.com

### Response Time
- Bug reports: 2-3 business days
- Feature requests: 1 week
- Pull requests: 3-5 business days

---

## 📚 Resources

### Helpful Links
- [Python Documentation](https://docs.python.org/3/)
- [BeautifulSoup Docs](https://www.crummy.com/software/BeautifulSoup/bs4/doc/)
- [Selenium Documentation](https://selenium-python.readthedocs.io/)
- [Hugging Face Transformers](https://huggingface.co/docs/transformers/)

### Learning Resources
- [Web Scraping Tutorial](https://realpython.com/beautiful-soup-web-scraper-python/)
- [Multi-Agent Systems](https://en.wikipedia.org/wiki/Multi-agent_system)
- [MIT License Explained](https://opensource.org/licenses/MIT)

---

## ❓ FAQ

**Q: Do I need permission to contribute?**  
A: No! OpenClaw is open source (MIT License). Fork and contribute freely.

**Q: Will my contribution be credited?**  
A: Yes! All contributors are recognized in CONTRIBUTORS.md and release notes.

**Q: Can I use OpenClaw in my commercial project?**  
A: Yes! MIT License allows commercial use. Just keep the license notice.

**Q: Can I create a paid service based on OpenClaw?**  
A: Yes, but you must:
  - Keep the MIT License notice
  - Credit Akash Rathod as the original creator
  - Make clear what you added vs. what's from OpenClaw

**Q: What if my PR is rejected?**  
A: Don't worry! We'll explain why and help you improve it.

---

## 📞 Contact

**Creator:** Akash Rathod  
**GitHub:** [@akash-rathod01](https://github.com/akash-rathod01)  
**LinkedIn:** [linkedin.com/in/akash-rathod01](https://linkedin.com/in/akash-rathod01)  
**Email:** akash.rathod01@example.com

---

**Thank you for contributing to OpenClaw!** 🚀

Your contributions help make research automation accessible to everyone, for FREE.

---

_Last updated: May 25, 2026_
