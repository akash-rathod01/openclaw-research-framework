# AI Summarization Feature - Complete Guide

## 🎉 What's New

**FREE AI-powered summarization** is now available! Automatically generate concise summaries of web-scraped content using state-of-the-art language models.

---

## ✨ Key Features

### 📝 Automatic Summarization
- Generates concise summaries of scraped web pages
- Uses facebook/bart-large-cnn model (best for web content)
- FREE forever - runs locally, no API costs
- Processes multiple pages in batch

### 🤖 Smart & Configurable
- Adjustable summary length (default: 150 words)
- Automatic fallback if AI fails (truncation)
- Skips very short content (< 100 chars)
- Preserves original content alongside summaries

### 💎 Zero Cost
- **$0 forever** - completely free
- No API keys required
- No rate limits or quotas
- No cloud dependencies

---

## 🚀 Quick Start

### Installation

First, install AI dependencies (one-time only):

```bash
pip install transformers torch
```

**Note:** First run will download the model (~1.6GB). This happens once and takes 1-2 minutes.

### Basic Usage

```bash
# Enable AI summarization
python orchestrator.py "https://www.nasa.gov" --summarize

# Limit pages and enable summarization
python orchestrator.py "https://example.com" --max-sources 10 --summarize

# Custom summary length (200 words max)
python orchestrator.py "https://example.com" --summarize --summary-length 200

# Combine with Tier 1 features
python orchestrator.py "https://example.com" --javascript --depth 3 --summarize
```

---

## 📊 What You Get

### Enhanced Reports

**HTML Dashboard:**
- 🤖 AI Summary badge on summarized pages
- Beautiful purple gradient summary boxes
- Original content still preserved
- Click links to verify sources

**Markdown Reports:**
- `🤖 AI Summary:` section for each page
- Clean, readable format
- Easy to share and version control

**JSON Data:**
- `summary` field in each source
- `summarized` boolean flag (true/false)
- `model` name used for summarization
- Full statistics tracking

---

## 🎯 Use Cases

### 1. Quick Research
```bash
python orchestrator.py "https://en.wikipedia.org/wiki/Artificial_Intelligence" --max-sources 20 --summarize
```
Get concise summaries of 20 Wikipedia pages in minutes instead of hours.

### 2. Competitive Analysis
```bash
python orchestrator.py "https://competitor.com" --depth 2 --max-sources 50 --summarize
```
Understand competitor website content at a glance.

### 3. Documentation Review
```bash
python orchestrator.py "https://docs.example.com" --summarize --summary-length 100
```
Generate short summaries of documentation pages.

### 4. News Aggregation
```bash
python orchestrator.py "https://news-site.com" --max-sources 30 --summarize
```
Quick overview of multiple news articles.

---

## ⚙️ Configuration

### Summary Length
Control how long summaries should be:

```bash
# Short summaries (50-100 words)
--summary-length 100

# Medium summaries (100-150 words) - DEFAULT
--summary-length 150

# Long summaries (150-250 words)
--summary-length 250
```

### Model Selection
Currently uses `facebook/bart-large-cnn` (best for web content).

Future versions will support:
- `t5-base` - Faster, general purpose
- `google/pegasus-xsum` - Extreme summarization
- OpenAI GPT models (PAID option)

---

## 📈 Performance

### Speed
- **First run:** 1-2 minutes model download (one-time)
- **Subsequent runs:** 2-5 seconds per page
- **Batch of 10 pages:** ~30-60 seconds
- **Batch of 100 pages:** ~5-10 minutes

### Model Size
- Disk space: ~2GB for model cache
- Memory: ~1GB RAM during summarization
- CPU usage: Moderate (no GPU required)

### Quality
- ⭐⭐⭐⭐⭐ News articles and blog posts
- ⭐⭐⭐⭐ General web content
- ⭐⭐⭐ Technical documentation
- ⭐⭐ Very short text (falls back to truncation)

---

## 🔍 Example Output

### Before (Original Content)
```
NASA has announced a groundbreaking new mission to Mars scheduled for launch in 2026. The mission, called Mars Exploration Rover 5 (MER-5), will carry advanced scientific instruments designed to search for signs of ancient microbial life. The rover will land in the Jezero Crater, a site believed to have once hosted a lake millions of years ago. Scientists are particularly interested in analyzing rock samples and mineral deposits that could provide clues about Mars' watery past. The mission will last approximately 2 years and cost an estimated $2.7 billion. NASA engineers have incorporated lessons learned from previous Mars missions to enhance the rover's capabilities...
[continues for 500+ words]
```

### After (AI Summary - 150 words)
```
🤖 AI Summary: NASA has announced a new Mars mission scheduled for 2026. The Mars Exploration Rover 5 (MER-5) will search for signs of ancient microbial life in Jezero Crater, a former lake site. The rover will analyze rock samples and mineral deposits to understand Mars' watery past. The mission will last 2 years and cost $2.7 billion.
```

---

## 💡 Tips & Best Practices

### When to Use Summarization

✅ **Good Use Cases:**
- Researching multiple sources (10+ pages)
- Quick overviews of lengthy content
- Team briefings and reports
- Content aggregation

❌ **Not Ideal For:**
- Very short pages (< 100 characters)
- Tables and structured data
- Code snippets and technical specs
- Already-concise content

### Optimizing Speed

1. **Limit sources** for faster results:
   ```bash
   --max-sources 20  # Instead of 100
   ```

2. **Combine with depth limits**:
   ```bash
   --depth 2 --max-sources 50 --summarize
   ```

3. **First run takes longer** (model download) - be patient!

### Quality Tips

1. **Adjust summary length** based on source length:
   - Short articles (300-500 words): `--summary-length 100`
   - Medium articles (500-1000 words): `--summary-length 150` (default)
   - Long articles (1000+ words): `--summary-length 200`

2. **Review summaries** in HTML reports - original content is preserved

3. **Use markdown exports** for team sharing

---

## 🆚 FREE vs PAID Comparison

| Feature | FREE (Hugging Face) | PAID (OpenAI GPT-4) |
|---------|---------------------|---------------------|
| **Cost** | $0 forever | ~$30/1000 pages |
| **Speed** | 2-5 sec/page | < 1 sec/page |
| **Quality** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Privacy** | Local (private) | Cloud (sent to OpenAI) |
| **Limits** | None | 60 requests/min |
| **Setup** | pip install | API key required |

**Recommendation:** Start with FREE. If quality isn't good enough after testing 10-20 sites, consider PAID.

---

## 🐛 Troubleshooting

### Model Download Fails

**Problem:** Download interrupted or failed

**Solution:**
```bash
python -c "from transformers import pipeline; pipeline('summarization', model='facebook/bart-large-cnn')"
```

This manually downloads the model.

### Out of Memory Error

**Problem:** RAM exceeded during summarization

**Solution:**
- Close other applications
- Reduce --max-sources to 10-20
- Summarize in smaller batches

### Slow Performance

**Problem:** Summarization taking too long

**Solution:**
- First run is always slow (model download)
- Subsequent runs should be 2-5 sec/page
- Consider using --max-sources to limit pages

### ImportError: transformers not found

**Problem:** Dependency not installed

**Solution:**
```bash
pip install transformers torch
```

---

## 📚 Advanced Usage

### Programmatic Access

```python
from skills.ai_summarization.summarizer import AISummarizer

# Initialize summarizer
summarizer = AISummarizer(model_name='facebook/bart-large-cnn')

# Summarize single text
summary = summarizer.summarize(
    text="Long article text here...",
    max_length=150,
    min_length=50
)

# Batch summarization
sources = [
    {'content': 'Article 1 content...'},
    {'content': 'Article 2 content...'}
]

summarized = summarizer.summarize_batch(
    sources=sources,
    max_length=150
)

# Access results
for source in summarized:
    if source['summarized']:
        print(f"Summary: {source['summary']}")
```

### Custom Models

Future support for custom models:

```python
# T5 model (faster, lower quality)
summarizer = AISummarizer(model_name='t5-base')

# PEGASUS (extreme summarization)
summarizer = AISummarizer(model_name='google/pegasus-xsum')
```

---

## 📖 Technical Details

### Model Information
- **Name:** facebook/bart-large-cnn
- **Size:** 1.63 GB
- **Architecture:** BART (Bidirectional and Auto-Regressive Transformers)
- **Training:** Fine-tuned on CNN/DailyMail dataset (news summarization)
- **Input limit:** ~3000 characters per page

### How It Works

1. **Lazy Loading:** Model loads only when first summary is requested
2. **Batch Processing:** Processes multiple sources sequentially
3. **Truncation:** Long content automatically truncated to 3000 chars
4. **Fallback:** If AI fails, uses simple truncation instead
5. **Caching:** Model cached for future use (no re-download)

### Error Handling
- Missing dependencies → Clear error message with install command
- AI failure → Automatic fallback to truncation
- Short content → Passes through without summarization
- Model load failure → Detailed error reporting

---

## 🔄 Backwards Compatibility

**100% compatible** with existing framework:
- ✅ Old commands still work exactly the same
- ✅ No summarization without `--summarize` flag
- ✅ Reports identical without the flag
- ✅ Zero breaking changes

### Migration Path
1. Install dependencies: `pip install transformers torch`
2. Add `--summarize` to existing commands
3. Test on small batch first (--max-sources 5)
4. Scale up once satisfied

---

## 📊 Statistics & Analytics

When summarization is enabled, reports include:

```json
{
  "ai_summarized": true,
  "summarization_stats": {
    "total_sources": 50,
    "summarized_count": 48,
    "model": "facebook/bart-large-cnn"
  }
}
```

Track:
- How many pages were successfully summarized
- Which model was used
- Success rate percentage

---

## 🎓 Learning Resources

### Understanding Summarization Models
- [BART Paper](https://arxiv.org/abs/1910.13461)
- [Hugging Face Transformers](https://huggingface.co/docs/transformers/)
- [Summarization Best Practices](https://huggingface.co/docs/transformers/tasks/summarization)

### Alternative Models
- [T5 Base](https://huggingface.co/t5-base)
- [PEGASUS](https://huggingface.co/google/pegasus-xsum)
- [GPT-4 Summarization](https://platform.openai.com/docs/guides/chat/introduction)

---

## 🚀 Future Enhancements

### Planned Features
- [ ] GPU acceleration for faster processing
- [ ] Multiple model support (T5, PEGASUS, GPT)
- [ ] Multi-language summarization (non-English)
- [ ] Extractive + Abstractive summary options
- [ ] Custom summary templates
- [ ] Keyword extraction integration

### Coming in Next Release
- [ ] Summary quality scoring
- [ ] A/B testing between models
- [ ] Cached summaries (avoid re-summarizing)

---

## 📝 Changelog

### v1.1.0 - AI Summarization (Current)
- ✨ Added FREE AI summarization with Hugging Face
- 🤖 facebook/bart-large-cnn model integration
- 📊 Enhanced HTML/Markdown reports with summaries
- 🎨 Beautiful purple gradient summary display
- ⚙️ CLI flags: --summarize, --summary-length
- 📚 Complete documentation and examples

---

## 🤝 Credits

- **Created by:** Akash Rathod
- **Framework:** OpenClaw v1.1.0
- **Model:** facebook/bart-large-cnn (Meta AI)
- **Libraries:** Hugging Face Transformers, PyTorch

---

## 💬 Support

### Questions?
- Check OVERVIEW.md for framework details
- Read TIER1_UPGRADE_SUMMARY.md for Tier 1 features
- Review SKILL.md in skills/ai_summarization/

### Issues?
- Verify dependencies: `pip list | grep -E "transformers|torch"`
- Test standalone: `python skills/ai_summarization/summarizer.py`
- Check model cache: `~/.cache/huggingface/hub/`

---

**Ready to try it? Run:**
```bash
python orchestrator.py "https://www.nasa.gov" --max-sources 10 --summarize
```

**🎉 Enjoy FREE AI-powered summarization!**
