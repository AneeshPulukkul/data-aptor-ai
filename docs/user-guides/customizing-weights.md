# Customizing Assessment Weights

This guide explains how to customize the weights of assessment modules to match your specific requirements.

## Understanding Weights

DataAptor AI uses a weighted scoring system where each module contributes to the overall AI readiness score. The default weights are:

| Module | Default Weight | Description |
|--------|----------------|-------------|
| Quality | 40% | Data quality fundamentals |
| Accessibility | 20% | Format and volume |
| Governance | 15% | Privacy and licensing |
| AI Compatibility | 20% | ML-specific factors |
| Diversity | 5% | Fairness and representation |

## When to Customize Weights

Consider customizing weights when:

1. **Compliance is Critical**: Increase Governance weight for regulated industries
2. **Quick Prototyping**: Increase Quality and Accessibility, decrease others
3. **Production ML**: Balance all modules, increase AI Compatibility
4. **Fairness-Focused**: Increase Diversity weight significantly
5. **Data Collection Phase**: Focus on Quality and Volume (Accessibility)

## Customization Methods

### Using the Web UI

1. Navigate to the Assessment page
2. Click "Customize Weights"
3. Adjust sliders for each module
4. Weights automatically normalize to 100%
5. Click "Save" to apply

### Using the CLI

```bash
# Specify individual weights
python dataaptor.py assess <dataset_id> \
  --weight-quality 0.30 \
  --weight-accessibility 0.25 \
  --weight-governance 0.20 \
  --weight-ai-compatibility 0.20 \
  --weight-diversity 0.05

# Use a preset profile
python dataaptor.py assess <dataset_id> --profile compliance
python dataaptor.py assess <dataset_id> --profile ml-production
python dataaptor.py assess <dataset_id> --profile fairness
```

### Using the API

```bash
curl -X POST http://localhost:8000/api/assessments \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "dataset_id": 1,
    "weights": {
      "quality": 0.30,
      "accessibility": 0.25,
      "governance": 0.20,
      "ai_compatibility": 0.20,
      "diversity": 0.05
    }
  }'
```

## Preset Profiles

DataAptor AI includes several preset weight profiles:

### Default Profile
Balanced for general AI/ML use cases.
```json
{
  "quality": 0.40,
  "accessibility": 0.20,
  "governance": 0.15,
  "ai_compatibility": 0.20,
  "diversity": 0.05
}
```

### Compliance Profile
For regulated industries (healthcare, finance).
```json
{
  "quality": 0.25,
  "accessibility": 0.15,
  "governance": 0.35,
  "ai_compatibility": 0.15,
  "diversity": 0.10
}
```

### ML Production Profile
For production machine learning systems.
```json
{
  "quality": 0.30,
  "accessibility": 0.20,
  "governance": 0.15,
  "ai_compatibility": 0.30,
  "diversity": 0.05
}
```

### Fairness Profile
For applications requiring fairness guarantees.
```json
{
  "quality": 0.25,
  "accessibility": 0.15,
  "governance": 0.20,
  "ai_compatibility": 0.15,
  "diversity": 0.25
}
```

### Quick Assessment Profile
For rapid initial evaluation.
```json
{
  "quality": 0.50,
  "accessibility": 0.30,
  "governance": 0.10,
  "ai_compatibility": 0.10,
  "diversity": 0.00
}
```

## Creating Custom Profiles

You can save custom weight configurations for reuse:

### Via CLI

```bash
# Save a custom profile
python dataaptor.py profile create my-profile \
  --weight-quality 0.35 \
  --weight-accessibility 0.20 \
  --weight-governance 0.25 \
  --weight-ai-compatibility 0.15 \
  --weight-diversity 0.05

# Use the custom profile
python dataaptor.py assess <dataset_id> --profile my-profile

# List available profiles
python dataaptor.py profile list

# Delete a profile
python dataaptor.py profile delete my-profile
```

### Via Configuration File

Create a `profiles.yaml` file:

```yaml
profiles:
  my-custom-profile:
    description: "Custom profile for my use case"
    weights:
      quality: 0.35
      accessibility: 0.20
      governance: 0.25
      ai_compatibility: 0.15
      diversity: 0.05
```

## Best Practices

1. **Start with Defaults**: Use default weights initially to establish a baseline
2. **Document Changes**: Record why you changed weights for future reference
3. **Be Consistent**: Use the same weights when comparing datasets
4. **Review Periodically**: Reassess weights as your requirements evolve
5. **Don't Zero Out**: Avoid setting any weight to 0 unless you have a specific reason

## Impact Analysis

When changing weights, consider the impact:

| Change | Effect |
|--------|--------|
| Increase Quality | More emphasis on data fundamentals |
| Increase Governance | Stricter compliance requirements |
| Increase AI Compatibility | Focus on ML-specific factors |
| Increase Diversity | Prioritize fairness metrics |
| Decrease any module | That aspect becomes less important in overall score |

## Next Steps

- Learn about [Report Interpretation](report-interpretation.md)
- Explore [Improving Readiness](improving-readiness.md)
- Review [Integration Options](integrations.md)
