# Tutorial: Assessing Image Datasets

This tutorial walks you through assessing an image dataset using DataAptor AI.

## Prerequisites

- DataAptor AI running (see [Installation Guide](../installation.md))
- An image dataset (folder of images or archive)
- CLI tool installed or access to Web UI

## Supported Image Formats

DataAptor AI supports:
- JPEG/JPG
- PNG
- BMP
- TIFF
- WebP

## Preparing Your Image Dataset

### Option 1: Folder Structure

Organize images by class for classification tasks:

```
my_dataset/
├── class_a/
│   ├── image001.jpg
│   ├── image002.jpg
│   └── ...
├── class_b/
│   ├── image001.jpg
│   ├── image002.jpg
│   └── ...
└── labels.csv  # Optional metadata
```

### Option 2: Flat Structure with Labels

```
my_dataset/
├── image001.jpg
├── image002.jpg
├── image003.jpg
└── labels.csv
```

Where `labels.csv` contains:

```csv
filename,label,additional_info
image001.jpg,cat,indoor
image002.jpg,dog,outdoor
image003.jpg,cat,outdoor
```

### Option 3: Archive File

Create a ZIP archive of your images:

```bash
zip -r my_dataset.zip my_dataset/
```

## Step 1: Upload the Dataset

### Using the CLI

```bash
# Upload a ZIP archive
python dataaptor.py upload my_dataset.zip

# Or upload with metadata
python dataaptor.py upload my_dataset.zip \
  --metadata '{"ai_task": "classification", "classes": ["cat", "dog"]}'
```

### Using the Web UI

1. Open http://localhost:3000
2. Click "Upload"
3. Drag and drop your ZIP file
4. Add metadata if needed
5. Click "Upload"

### Using the API

```bash
curl -X POST http://localhost:8000/api/datasets/upload \
  -H "Authorization: Bearer <your-token>" \
  -F "file=@my_dataset.zip" \
  -F "name=Image Classification Dataset"
```

## Step 2: Start the Assessment

```bash
# Start assessment
python dataaptor.py assess <dataset_id>

# Or with specific modules
python dataaptor.py assess <dataset_id> \
  --modules quality,accessibility,ai_compatibility
```

## Step 3: Understanding Image-Specific Metrics

### Quality Assessment for Images

The quality module evaluates:

| Criterion | What It Checks |
|-----------|----------------|
| Completeness | Missing images, corrupt files |
| Accuracy | Image quality (blur, noise, exposure) |
| Consistency | Resolution uniformity, aspect ratios |
| Timeliness | File modification dates |

Example output:

```
Quality Assessment Results:
- Completeness: 98% (2 corrupt files detected)
- Accuracy: 85% (15% of images have quality issues)
  - 5 images are blurry
  - 3 images are overexposed
  - 2 images have high noise
- Consistency: 70% (multiple resolutions detected)
  - 60% at 1920x1080
  - 30% at 1280x720
  - 10% at various sizes
- Timeliness: 100% (all images from last 6 months)
```

### Accessibility Assessment for Images

| Criterion | What It Checks |
|-----------|----------------|
| Format | Image format compatibility |
| Volume | Number of images per class |

Example output:

```
Accessibility Assessment Results:
- Format: 100% (all JPEG - fully compatible)
- Volume: 75%
  - Total images: 5,000
  - Minimum recommended: 1,000 per class
  - Class distribution:
    - cat: 3,000 images (adequate)
    - dog: 2,000 images (adequate)
```

### AI Compatibility for Images

| Criterion | What It Checks |
|-----------|----------------|
| Relevance | Image content matches task |
| Labeling | Label quality and coverage |
| Features | Visual feature diversity |
| Preprocessing | Normalization needs |

Example output:

```
AI Compatibility Assessment Results:
- Relevance: 90% (images match classification task)
- Labeling: 95% (all images labeled, 5% ambiguous)
- Feature Richness: 80%
  - Good variety in backgrounds
  - Multiple angles represented
  - Various lighting conditions
- Preprocessing: 85%
  - Resize needed (multiple resolutions)
  - Normalization recommended
```

### Diversity Assessment for Images

| Criterion | What It Checks |
|-----------|----------------|
| Representativeness | Visual diversity |
| Bias | Class balance, demographic representation |

Example output:

```
Diversity Assessment Results:
- Representativeness: 75%
  - Indoor/outdoor balance: 60/40
  - Lighting variety: good
  - Background diversity: moderate
- Bias: 80%
  - Class balance: 60/40 (slight imbalance)
  - No significant visual bias detected
```

## Step 4: View and Export Report

```bash
# View report
python dataaptor.py report <assessment_id>

# Export as HTML with visualizations
python dataaptor.py export <assessment_id> --format html --output image_report.html
```

The HTML report includes:
- Sample images from each class
- Quality issue examples
- Distribution charts
- Recommendations with visual examples

## Common Issues and Solutions

### Issue: Low Quality Score

**Problem**: Many images flagged as blurry or low quality

**Solution**:
```python
from PIL import Image
import cv2
import numpy as np

def check_blur(image_path, threshold=100):
    """Check if image is blurry using Laplacian variance."""
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    variance = cv2.Laplacian(img, cv2.CV_64F).var()
    return variance < threshold

# Filter out blurry images
import os
good_images = []
for img_file in os.listdir('my_dataset'):
    if not check_blur(f'my_dataset/{img_file}'):
        good_images.append(img_file)
```

### Issue: Inconsistent Resolutions

**Problem**: Images have varying resolutions

**Solution**:
```python
from PIL import Image
import os

def resize_images(input_dir, output_dir, target_size=(224, 224)):
    """Resize all images to target size."""
    os.makedirs(output_dir, exist_ok=True)
    
    for img_file in os.listdir(input_dir):
        img_path = os.path.join(input_dir, img_file)
        img = Image.open(img_path)
        img_resized = img.resize(target_size, Image.LANCZOS)
        img_resized.save(os.path.join(output_dir, img_file))

resize_images('my_dataset', 'my_dataset_resized')
```

### Issue: Class Imbalance

**Problem**: Uneven distribution of images across classes

**Solution**:
```python
from tensorflow.keras.preprocessing.image import ImageDataGenerator

# Data augmentation for minority class
datagen = ImageDataGenerator(
    rotation_range=20,
    width_shift_range=0.2,
    height_shift_range=0.2,
    horizontal_flip=True,
    fill_mode='nearest'
)

# Generate augmented images
img = load_img('minority_class/image.jpg')
x = img_to_array(img)
x = x.reshape((1,) + x.shape)

i = 0
for batch in datagen.flow(x, batch_size=1, save_to_dir='augmented', 
                          save_prefix='aug', save_format='jpg'):
    i += 1
    if i >= 10:  # Generate 10 augmented versions
        break
```

### Issue: Missing Labels

**Problem**: Some images don't have labels

**Solution**:
```python
import os
import pandas as pd

# Create labels from folder structure
labels = []
for class_name in os.listdir('my_dataset'):
    class_dir = os.path.join('my_dataset', class_name)
    if os.path.isdir(class_dir):
        for img_file in os.listdir(class_dir):
            labels.append({
                'filename': f'{class_name}/{img_file}',
                'label': class_name
            })

df = pd.DataFrame(labels)
df.to_csv('my_dataset/labels.csv', index=False)
```

## Best Practices for Image Datasets

1. **Consistent Resolution**: Resize all images to the same dimensions
2. **Quality Control**: Remove blurry, corrupt, or low-quality images
3. **Balanced Classes**: Aim for similar numbers of images per class
4. **Diverse Samples**: Include variety in lighting, angles, backgrounds
5. **Clear Labels**: Ensure all images have accurate labels
6. **Metadata**: Include relevant metadata (source, date, conditions)

## Next Steps

- Try the [ML Pipeline Integration Tutorial](ml-pipeline-integration.md)
- Learn about [Improving Readiness](../improving-readiness.md)
- Review [Customizing Weights](../customizing-weights.md)
