# AI Summarization Skill

## Overview
AI-powered text summarization using Hugging Face transformers. Generates concise summaries of web-scraped content automatically.

## Version
- **Type**: FREE (No API costs)
- **Model**: facebook/bart-large-cnn (default)
- **Cost**: $0 forever
- **Speed**: ~2-5 seconds per page

## Capabilities
- ✅ Automatic text summarization
- ✅ Batch processing (multiple sources)
- ✅ Configurable summary length
- ✅ Multiple model options
- ✅ Fallback handling (truncation if AI fails)
- ✅ Privacy-preserving (runs locally)

## Dependencies
```bash
pip install transformers torch
```

## Usage

### From Orchestrator
```bash
# Enable AI summarization
python orchestrator.py "https://example.com" --summarize

# Custom summary length
python orchestrator.py "https://example.com" --summarize --summary-length 200
```

### Programmatic
```python
from skills.ai_summarization.summarizer import AISummarizer

summarizer = AISummarizer()
summary = summarizer.summarize(text, max_length=150, min_length=50)
```

## Models Available

| Model | Best For | Speed | Quality |
|-------|----------|-------|---------|
| facebook/bart-large-cnn | Web content, articles | Medium | ⭐⭐⭐⭐⭐ |
| t5-base | General purpose | Fast | ⭐⭐⭐⭐ |
| google/pegasus-xsum | Extreme short summaries | Medium | ⭐⭐⭐⭐ |

## Configuration

### Default Settings
- Max length: 150 words
- Min length: 50 words
- Model: facebook/bart-large-cnn
- Device: CPU

### OpenClaw Integration
Registered in `AGENTS.md`:
```markdown
## ai_summarization
- **Path**: `skills/ai_summarization/summarizer.py`
- **Function**: `research(topic, sources=[], max_length=150, min_length=50)`
- **Purpose**: Generate AI summaries of scraped content
```

## Performance

### Speed
- First run: 30-60 seconds (downloads model)
- Subsequent runs: 2-5 seconds per page
- 100 pages: ~5-10 minutes

### Accuracy
- High quality for web articles
- Medium quality for technical docs
- Lower quality for very short text (< 100 chars)

## Error Handling
- ✅ Automatic fallback to truncation if AI fails
- ✅ Graceful degradation for short text
- ✅ Import error detection (missing dependencies)
- ✅ Model loading error handling

## Example Output

**Original (500 chars):**
> "Artificial intelligence (AI) is intelligence demonstrated by machines, in contrast to the natural intelligence displayed by humans and animals. Leading AI textbooks define the field as the study of 'intelligent agents': any device that perceives its environment and takes actions that maximize its chance of successfully achieving its goals..."

**Summary (80 chars):**
> "AI is intelligence by machines that perceive environments and achieve goals."

## Limitations
- ⚠️ Requires ~2GB disk space for model
- ⚠️ CPU-only (slower than GPU)
- ⚠️ Input limited to ~3000 characters
- ⚠️ English language only

## Future Enhancements
- [ ] GPU support for faster processing
- [ ] Multi-language support
- [ ] Custom model fine-tuning
- [ ] OpenAI GPT integration (PAID option)
