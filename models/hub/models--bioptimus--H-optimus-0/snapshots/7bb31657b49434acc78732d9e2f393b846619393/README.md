---
tags:
- image-feature-extraction
- timm
- pathology
- histology
- medical imaging
- self-supervised learning
- vision transformer
- foundation model
library_name: timm
license: apache-2.0
---

# Model card for H-optimus-0

<p align="center">
<img src="./logo.png" width="500" height="180" />
</p>

`H-optimus-0` is an open-source foundation model for histology, developed by [Bioptimus](https://www.bioptimus.com/).
The model is a 1.1B parameter vision transformer trained on a proprietary collection of more than 500,000 H&E stained whole slide histology images.
For more information, please refer to our GitHub repository [here](https://github.com/bioptimus/releases/tree/main/models/h-optimus/v0?utm_source=owkin&utm_medium=referral&utm_campaign=h-bioptimus-o).

`H-optimus-0` can be used to extract powerful features from histology images for various downstream applications, such as mutation prediction, survival analysis, or tissue classification.

## How to use it to extract features.

The code below can be used to run inference; `H-optimus-0` expects images of size 224x224 that were extracted at 0.5 microns per pixel.
```python
from huggingface_hub import login
import torch
import timm 
from torchvision import transforms

# Login to the Hugging Face hub, using your user access token that can be found here:
# https://huggingface.co/settings/tokens.
login()

model = timm.create_model(
    "hf-hub:bioptimus/H-optimus-0", pretrained=True, init_values=1e-5, dynamic_img_size=False
)
model.to("cuda")
model.eval()

transform = transforms.Compose([
    transforms.ToTensor(),
    transforms.Normalize(
        mean=(0.707223, 0.578729, 0.703617), 
        std=(0.211883, 0.230117, 0.177517)
    ),
])

input = torch.rand(3, 224, 224)
input = transforms.ToPILImage()(input)

# We recommend using mixed precision for faster inference.
with torch.autocast(device_type="cuda", dtype=torch.float16):
    with torch.inference_mode():
        features = model(transform(input).unsqueeze(0).to("cuda"))

assert features.shape == (1, 1536)
```

## BibTeX entry and citation info.

If you find this repository useful, please consider citing our work:
```
@software{hoptimus0,
  author = {Saillard, Charlie and Jenatton, Rodolphe and Llinares-López, Felipe and Mariet, Zelda and Cahané, David and Durand, Eric and Vert, Jean-Philippe},
  title = {H-optimus-0},
  url = {https://github.com/bioptimus/releases/tree/main/models/h-optimus/v0},
  year = {2024},
}
```