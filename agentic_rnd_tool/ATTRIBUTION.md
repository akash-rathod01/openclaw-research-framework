# Third-Party Licenses & Attribution

This project uses the following open-source libraries. We are grateful to their maintainers and contributors.

---

## Core Dependencies

### **Python Standard Library**
- **License:** Python Software Foundation License
- **Used for:** Core functionality (json, datetime, logging, etc.)

### **requests** - HTTP Library
- **Version:** 2.31.0+
- **License:** Apache License 2.0
- **Repository:** https://github.com/psf/requests
- **Used for:** HTTP requests and web scraping

### **beautifulsoup4** - HTML/XML Parser
- **Version:** 4.12.0+
- **License:** MIT License
- **Repository:** https://www.crummy.com/software/BeautifulSoup/
- **Used for:** HTML parsing and data extraction

### **selenium** - Browser Automation
- **Version:** 4.0.0+
- **License:** Apache License 2.0
- **Repository:** https://github.com/SeleniumHQ/selenium
- **Used for:** JavaScript rendering and dynamic page scraping

### **rich** - Terminal Formatting
- **Version:** 13.7.0+
- **License:** MIT License
- **Repository:** https://github.com/Textualize/rich
- **Used for:** Beautiful console output and progress bars

---

## AI Summarization Dependencies

### **transformers** - Hugging Face Transformers
- **Version:** 4.48.1+
- **License:** Apache License 2.0
- **Repository:** https://github.com/huggingface/transformers
- **Used for:** FREE AI text summarization
- **Model:** facebook/bart-large-cnn (also Apache 2.0)

### **torch (PyTorch)** - Deep Learning Framework
- **Version:** 2.11.0+
- **License:** BSD 3-Clause License
- **Repository:** https://github.com/pytorch/pytorch
- **Used for:** Running AI models (CPU-only in this project)

---

## Additional Dependencies

### **lxml** - XML/HTML Processing
- **License:** BSD License
- **Repository:** https://github.com/lxml/lxml
- **Used for:** Fast XML/HTML parsing

### **urllib3** - HTTP Client
- **License:** MIT License
- **Used for:** Low-level HTTP operations (via requests)

---

## Development Tools

### **Git** - Version Control
- **License:** GPL v2
- **Used for:** Version control (not bundled with software)

---

## License Compatibility Summary

All dependencies are compatible with MIT License:
- ✅ MIT License (beautifulsoup4, rich, urllib3)
- ✅ Apache License 2.0 (requests, selenium, transformers)
- ✅ BSD License (PyTorch, lxml)

**No licensing conflicts!** This project can be safely released under MIT License.

---

## AI Model Attribution

### **BART Model** (facebook/bart-large-cnn)
- **Model Card:** https://huggingface.co/facebook/bart-large-cnn
- **Paper:** "BART: Denoising Sequence-to-Sequence Pre-training for Natural Language Generation, Translation, and Comprehension"
- **Authors:** Mike Lewis, Yinhan Liu, Naman Goyal, et al. (Facebook AI)
- **License:** Apache License 2.0
- **Training Data:** CNN/DailyMail dataset
- **Used for:** Text summarization in this project

---

## Framework Attribution

### **OpenClaw Inspiration**
This project's multi-agent architecture was inspired by OpenClaw-style agent orchestration patterns, adapted for web research and AI summarization use cases.

---

## Special Thanks

- **Hugging Face** - For providing FREE, open-source AI models
- **Python Community** - For amazing libraries and ecosystem
- **Open Source Contributors** - For making this project possible

---

*Last Updated: March 25, 2026*  
*For questions about licensing, see the project repository*
