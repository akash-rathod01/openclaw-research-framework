# 🎓 Complete Training Guide: Fine-Tune OpenClaw AI Summarizer

**Estimated Time:** 3-5 hours (most time is passive training)  
**Requirements:** Gaming laptop with GPU (RTX 3060+ recommended) or Google Colab

---

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [Installation](#installation)
3. [Step-by-Step Training Process](#step-by-step-training-process)
4. [Integration](#integration)
5. [Troubleshooting](#troubleshooting)
6. [FAQ](#faq)

---

## Prerequisites

### Hardware Requirements

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| **GPU** | RTX 3050 (4GB VRAM) | RTX 3060+ (6GB+ VRAM) |
| **RAM** | 16GB | 32GB |
| **Storage** | 10GB free | 20GB+ free |
| **OS** | Windows 10/11 | Windows 11 |

### Software Requirements

- **Python 3.8+** (Python 3.13 recommended)
- **CUDA 11.7+** (for NVIDIA GPU)
- **Git** (for version control)

### Check Your GPU

```bash
# Windows PowerShell
nvidia-smi

# Look for:
# - GPU Name (e.g., NVIDIA GeForce RTX 3060)
# - Memory (e.g., 6144MiB / 6144MiB)
```

---

## Installation

### Step 1: Navigate to Training Directory

```powershell
cd D:\LATEST_GENAI_AGENTIC_PROJECTS\agentic_rnd_tool\agentic_rnd_tool\training
```

### Step 2: Install Training Dependencies

```powershell
# Install all training requirements
pip install -r training_requirements.txt

# This installs:
# - transformers (Hugging Face)
# - torch (PyTorch with CUDA support)
# - datasets
# - rouge-score
# - and more...
```

**Installation time:** 5-10 minutes (downloads ~3GB)

### Step 3: Download spaCy Model (for NER validation)

```powershell
python -m spacy download en_core_web_sm
```

---

## Step-by-Step Training Process

### Phase 1: Data Preparation (10-15 minutes)

#### Step 1: Extract Training Data from Your Reports

You should have existing scraping reports in `agentic_rnd_tool/reports/` from your CIA, IIT Bombay, and other tests.

```powershell
# Run the data extraction script
python training_data_creator.py
```

**Expected Output:**
```
🎓 OpenClaw Training Data Creator

Step 1: Extracting training data from reports...
Found 14 report files
[████████████████████] 100%

Step 2: Filtering high-quality samples...
Filtered: 85/150 samples (>= high quality)
Filtered: 142/150 samples (>= medium quality)

Step 3: Generating statistics...
📊 Dataset Statistics:
  Total samples: 142
  Quality distribution: {'high': 85, 'medium': 57, 'low': 8}
  Unique sources: 45
  Avg original length: 1,247 chars
  Avg summary length: 124 chars
  Avg compression: 9.9%

Step 4: Saving datasets...
✅ Saved 85 training samples to training_data_high_quality.json
✅ Saved 142 training samples to training_data_medium_quality.json
✅ Saved 150 training samples to training_data_all.json

✅ Training data preparation complete!

💡 Recommended: Use 'training_data_medium_quality.json' for fine-tuning
   Contains 142 samples with balanced quality
```

**What This Does:**
- Reads all your `*.json` reports
- Extracts (original_content, AI_summary) pairs
- Filters by quality (compression ratio, length, etc.)
- Creates 3 datasets: high, medium, and all quality

**Files Created:**
- `training_data_high_quality.json` - 85 best samples (strictest quality)
- `training_data_medium_quality.json` - 142 samples (recommended)
- `training_data_all.json` - All 150 samples

#### Step 2: Review Training Data (Optional)

```powershell
# Open in text editor to inspect
notepad training_data_medium_quality.json
```

**Sample Format:**
```json
[
  {
    "document": "The Central Intelligence Agency (CIA) is a civilian foreign intelligence service...",
    "summary": "The CIA is a US foreign intelligence agency with 160+ careers...",
    "source": "https://www.cia.gov/careers/",
    "title": "Careers - CIA",
    "quality": "high",
    "original_length": 3621,
    "summary_length": 128,
    "compression_ratio": 0.0353
  },
  ...
]
```

---

### Phase 2: Model Training (2-4 hours - Passive)

#### Step 3: Start Training

```powershell
# Basic training (3 epochs, auto-detect GPU settings)
python fine_tune_summarizer.py --data training_data_medium_quality.json

# Advanced options:
# More epochs (better quality, longer time)
python fine_tune_summarizer.py --data training_data_medium_quality.json --epochs 5

# Custom output directory
python fine_tune_summarizer.py --data training_data_medium_quality.json --output ./my_model

# Smaller batch size (if GPU runs out of memory)
python fine_tune_summarizer.py --data training_data_medium_quality.json --batch-size 2
```

**Expected Output:**
```
====================================================================
🎓 OpenClaw AI Fine-Tuning System
====================================================================

🖥️  Hardware Detection
Device: cuda
GPU: NVIDIA GeForce RTX 3060 Laptop GPU

📥 Loading pre-trained BART model...
This may take 1-2 minutes (downloading 1.6GB model)
✓ Model loaded successfully!

📊 Loading training data from: training_data_medium_quality.json
Loaded 142 training samples
Splitting dataset: 80% train, 10% validation, 10% test
✓ Train: 113 samples
✓ Validation: 15 samples
✓ Test: 14 samples

🔄 Preprocessing datasets (tokenizing)...
Tokenizing train: 100%|████████████████| 113/113 [00:12<00:00]
Tokenizing validation: 100%|██████████| 15/15 [00:01<00:00]
Tokenizing test: 100%|███████████████| 14/14 [00:01<00:00]

⚙️  Configuring training parameters...
GPU Memory: 6.0 GB
Using batch_size=4

====================================================================
🚀 Starting fine-tuning...
====================================================================
This will take 2-4 hours on GPU, 8-12 hours on CPU
You can close this window - training will continue

Epoch 1/3
Training: 100%|██████████████| 29/29 [15:32<00:00, 32.14s/it]
Evaluation: 100%|████████████| 4/4 [00:45<00:00, 11.25s/it]
  train_loss: 1.234
  eval_loss: 0.987
  eval_rouge1: 0.412
  eval_rouge2: 0.189
  eval_rougeL: 0.387
  
Epoch 2/3
Training: 100%|██████████████| 29/29 [15:28<00:00, 32.00s/it]
Evaluation: 100%|████████████| 4/4 [00:44<00:00, 11.10s/it]
  train_loss: 0.876
  eval_loss: 0.823
  eval_rouge1: 0.438
  eval_rouge2: 0.207
  eval_rougeL: 0.415
  ✅ New best model! (ROUGE-L: 0.415)
  
Epoch 3/3
Training: 100%|██████████████| 29/29 [15:30<00:00, 32.07s/it]
Evaluation: 100%|████████████| 4/4 [00:44<00:00, 11.15s/it]
  train_loss: 0.654
  eval_loss: 0.789
  eval_rouge1: 0.445
  eval_rouge2: 0.215
  eval_rougeL: 0.421
  ✅ New best model! (ROUGE-L: 0.421)

📊 Evaluating on test set...

✅ Test Results:
  ROUGE-1: 0.4423
  ROUGE-2: 0.2134
  ROUGE-L: 0.4189
  Compression: 10.2%
  Avg Length: 127 words

💾 Saving fine-tuned model to ./fine_tuned_model/final

✅ Training complete! Model saved to ./fine_tuned_model/final
```

**What's Happening:**
1. **Epoch 1:** Model learning from your data (basic patterns)
2. **Epoch 2:** Model improving quality (better summaries)
3. **Epoch 3:** Model fine-tuning details (best summaries)
4. **Auto-save:** Best checkpoint saved (highest ROUGE-L score)

**Training Time:**
- **RTX 3060** (6GB): ~2-3 hours
- **RTX 3070** (8GB): ~1.5-2 hours
- **RTX 4090** (24GB): ~45-60 minutes
- **CPU only**: ~8-12 hours

**Can You Close the Window?**
- ✅ **Yes** - Training continues in background
- ⚠️ **BUT** - You won't see progress updates
- 💡 **Better** - Let it run, check back periodically

---

### Phase 3: Validation (15-20 minutes)

#### Step 4: Validate Model Quality

After training completes, validate the model meets all standards:

```powershell
python validation_pipeline.py --model ./fine_tuned_model/final --test-data training_data_medium_quality.json
```

**Expected Output:**
```
====================================================================
📋 FULL VALIDATION REPORT
====================================================================

📦 Loading models for validation...
Loading fine-tuned model from: ./fine_tuned_model/final
✓ Fine-tuned model loaded
Loading baseline model: facebook/bart-large-cnn
✓ Baseline model loaded

1️⃣  Improvement over Baseline
🔍 Validating model improvement (50 samples)...
Testing on 50 samples

┌─────────────────────────────────────────────────────────┐
│                    Model Comparison                      │
├────────────┬────────────┬─────────────┬─────────────────┤
│ Metric     │ Baseline   │ Fine-tuned  │ Improvement     │
├────────────┼────────────┼─────────────┼─────────────────┤
│ ROUGE1     │ 0.3842     │ 0.4423      │ ✅ +0.0581      │
│ ROUGE2     │ 0.1654     │ 0.2134      │ ✅ +0.0480      │
│ ROUGEL     │ 0.3521     │ 0.4189      │ ✅ +0.0668      │
└────────────┴────────────┴─────────────┴─────────────────┘

Overall Improvement: ✅ PASS

2️⃣  Global AI Standards
┌────────────────────────────────────────────────────────────┐
│                   Industry Benchmarks                       │
├────────────┬────────────┬────────────────┬────────────────┤
│ Metric     │ Score      │ Min Threshold  │ Status         │
├────────────┼────────────┼────────────────┼────────────────┤
│ ROUGE1     │ 0.4423     │ ≥ 0.35         │ ✅ PASS        │
│ ROUGE2     │ 0.2134     │ ≥ 0.15         │ ✅ PASS        │
│ ROUGEL     │ 0.4189     │ ≥ 0.30         │ ✅ PASS        │
└────────────┴────────────┴────────────────┴────────────────┘

Global Standards: ✅ PASS

3️⃣  Application Requirements
🎯 Validating application requirements (20 samples)...

┌───────────────────────────────────────────────────────────┐
│                  OpenClaw Requirements                     │
├───────────────────────┬────────────┬─────────┬───────────┤
│ Requirement           │ Score      │ Target  │ Status    │
├───────────────────────┼────────────┼─────────┼───────────┤
│ Compression Ratio     │ 10%        │ 5%-15%  │ ✅ PASS   │
│ Informativeness       │ 0.78       │ ≥ 0.70  │ ✅ PASS   │
│ Factual Consistency   │ 94%        │ ≥ 90%   │ ✅ PASS   │
│ Overall Quality       │ 0.82       │ ≥ 0.75  │ ✅ PASS   │
└───────────────────────┴────────────┴─────────┴───────────┘

Application Requirements: ✅ PASS

====================================================================
┌──────────────────────────────────────────────────────────────┐
│              ✅ VALIDATION PASSED                             │
│                                                               │
│  🎉 MODEL READY FOR PRODUCTION                               │
│                                                               │
│  The fine-tuned model meets all requirements:                │
│  ✅ Outperforms baseline by >5% on ROUGE-L                   │
│  ✅ Meets global AI industry standards                       │
│  ✅ Satisfies application-specific requirements              │
│                                                               │
│  Next Steps:                                                 │
│  1. Update skills/ai_summarization/summarizer.py            │
│  2. Test on live websites                                    │
│  3. Monitor performance in production                        │
└──────────────────────────────────────────────────────────────┘
====================================================================
```

**What This Checks:**
1. **Improvement:** Fine-tuned > Baseline (+5% minimum)
2. **Global Standards:** ROUGE scores meet industry benchmarks
3. **App Requirements:** Compression, consistency, quality targets

**If Validation Fails:**
- **Train longer:** Try 5-7 epochs instead of 3
- **More data:** Scrape more websites to get 200+ samples
- **Better quality:** Filter for `high_quality` data only

---

## Integration

### Step 5: Update OpenClaw to Use Fine-Tuned Model

#### Method 1: Update Summarizer Code (Recommended)

Open `agentic_rnd_tool/skills/ai_summarization/summarizer.py` and change line 22:

**Before:**
```python
def __init__(self, model_name: str = "facebook/bart-large-cnn"):
```

**After:**
```python
def __init__(self, model_name: str = "../../training/fine_tuned_model/final"):
```

#### Method 2: Absolute Path (If Relative Path Issues)

```python
def __init__(self, model_name: str = "D:/LATEST_GENAI_AGENTIC_PROJECTS/agentic_rnd_tool/agentic_rnd_tool/training/fine_tuned_model/final"):
```

### Step 6: Test Fine-Tuned Model

```powershell
cd ..  # Go back to agentic_rnd_tool directory
python orchestrator.py "https://www.nasa.gov" --max-sources 10 --summarize --javascript
```

**Compare Results:**
- **Before:** Generic summaries, sometimes verbose
- **After:** More concise, web-optimized summaries

---

## Troubleshooting

### Issue 1: Out of GPU Memory

**Error:**
```
RuntimeError: CUDA out of memory. Tried to allocate 512.00 MiB
```

**Solution 1:** Reduce batch size
```powershell
python fine_tune_summarizer.py --data training_data_medium_quality.json --batch-size 2
```

**Solution 2:** Use smaller model (not recommended)
```python
# In fine_tune_summarizer.py, line 27, change to:
model_name = "facebook/bart-base"  # Smaller, faster, but less accurate
```

### Issue 2: Training Too Slow

**Symptoms:** 1 epoch takes > 2 hours

**Check GPU Usage:**
```powershell
nvidia-smi
```

**Solutions:**
1. **Close other GPU apps** (games, Chrome, etc.)
2. **Update GPU drivers**
3. **Verify CUDA installed:** `nvcc --version`
4. **Reinstall PyTorch with CUDA:**
   ```powershell
   pip uninstall torch
   pip install torch --index-url https://download.pytorch.org/whl/cu118
   ```

### Issue 3: Model Not Improving

**Symptoms:** ROUGE-L doesn't increase after epoch 1

**Solutions:**
1. **More epochs:** Train for 5-7 epochs
2. **Lower learning rate:**
   ```python
   # In fine_tune_summarizer.py, line 192, change to:
   learning_rate=1e-5,  # Was 2e-5
   ```
3. **More data:** Scrape 200+ pages for training

### Issue 4: Validation Fails

**Symptoms:** "⚠️ MODEL NEEDS IMPROVEMENT"

**Common Causes:**
- Not enough training data (< 100 samples)
- Low quality data (compression ratio too high/low)
- Training stopped too early

**Solutions:**
1. **Check data quality:**
   ```powershell
   python training_data_creator.py
   # Look at "Quality distribution" - need > 80 high/medium samples
   ```
2. **Train longer:** 5-7 epochs
3. **Use high_quality data:**
   ```powershell
   python fine_tune_summarizer.py --data training_data_high_quality.json --epochs 5
   ```

---

## FAQ

**Q: Do I need to train on Google Colab?**  
A: No! If you have a gaming laptop with RTX 3050+, train locally. It's faster and free.

**Q: How much does training cost?**  
A: $0 if you have a GPU locally. Google Colab Free is also $0 but slower.

**Q: Can I train on CPU?**  
A: Yes, but it takes 8-12 hours instead of 2-4 hours.

**Q: Will this work with my RTX 3050?**  
A: Yes! Use `--batch-size 2` to fit in 4GB VRAM.

**Q: Can I pause training and resume later?**  
A: Yes! Training saves checkpoints every 100 steps. If interrupted, re-run the same command and it will resume.

**Q: How do I know if training is working?**  
A: Watch `eval_rougeL` - it should increase from ~0.35 → 0.42 over epochs.

**Q: Should I use all my scraping data?**  
A: Use medium_quality (balanced). High_quality has fewer samples but stricter standards.

**Q: Can I fine-tune again later with more data?**  
A: Yes! Just add more scraping data and re-run training. It will further improve.

---

## Next Steps

After successful training and integration:

1. **Test on various websites** - Try government, academic, news sites
2. **Compare side-by-side** - Run baseline vs fine-tuned, see improvements
3. **Monitor performance** - Track summary quality over time
4. **Iterate** - Collect more data, retrain periodically

**Congratulations! You've successfully fine-tuned an AI model to global standards!** 🎉

---

**Need Help?**  
- Check [validation_pipeline.py output](#phase-3-validation-15-20-minutes)
- Review [troubleshooting section](#troubleshooting)
- Open an issue on GitHub with training logs
