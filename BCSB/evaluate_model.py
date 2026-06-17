
import os
import torch
import torch.nn as nn
from torchvision import transforms
from torchvision.models import efficientnet_b3, EfficientNet_B3_Weights
from torch.utils.data import Dataset, DataLoader
from PIL import Image
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
import argparse

# Configuration
DEVICE = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
NUM_CLASSES = 3
CLASS_NAMES = ['Underweight', 'Healthy', 'Overweight']
BCS_MAP = {'underweight': 0, 'healthy': 1, 'overweight': 2}
MODEL_PATH = 'bcs_cropped_model.pth'  # Default model path

# Transforms (Must match training)
test_transform = transforms.Compose([
    transforms.Resize(320),
    transforms.CenterCrop(300),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
])

class BCSDataset(Dataset):
    def __init__(self, df, transform=None):
        self.df = df.reset_index(drop=True)
        self.transform = transform

    def __len__(self):
        return len(self.df)

    def __getitem__(self, idx):
        row = self.df.iloc[idx]
        img_path = row['image_path']
        try:
            img = Image.open(img_path).convert('RGB')
            if self.transform:
                img = self.transform(img)
            label = torch.tensor(row['bcs_label'], dtype=torch.long)
            return img, label, img_path
        except Exception as e:
            print(f"Error loading image {img_path}: {e}")
            # Return a dummy tensor or handle error appropriately in a real scenario
            # Here we just return None to filter later if needed (simple dataloader might crash)
            # For simplicity, we'll assume dataset is clean or let it crash to debug
            raise e

def load_data_dataframe(base_dir):
    age_groups = ['puppy', 'adult', 'senior']
    df_list = []

    print(f"Scanning dataset at: {base_dir}")
    if not os.path.exists(base_dir):
        print(f"Error: Dataset directory not found at {base_dir}")
        return pd.DataFrame()

    for age in age_groups:
        age_dir = os.path.join(base_dir, age)
        if not os.path.exists(age_dir):
            continue

        for bcs_folder in os.listdir(age_dir):
            bcs_dir = os.path.join(age_dir, bcs_folder)
            if not os.path.isdir(bcs_dir) or bcs_folder not in BCS_MAP:
                continue

            label = BCS_MAP[bcs_folder]
            
            for breed_folder in os.listdir(bcs_dir):
                breed_dir = os.path.join(bcs_dir, breed_folder)
                if not os.path.isdir(breed_dir):
                    continue

                for img_file in os.listdir(breed_dir):
                    if img_file.lower().endswith(('.jpg', '.jpeg', '.png')):
                        img_path = os.path.join(breed_dir, img_file)
                        df_list.append({
                            'image_path': img_path,
                            'bcs_label': label,
                            'age': age,
                            'breed': breed_folder
                        })
    
    return pd.DataFrame(df_list)

def load_model(model_path):
    print(f"Loading model architecture (EfficientNet B3)...")
    model = efficientnet_b3(weights=None) # Start with no weights to avoid downloading if not needed, we load state_dict anyway
    # But wait, if we load state_dict, we need the architecture to match.
    # The original code loaded default weights then modified classifier.
    # We should reproduce that structure.
    model = efficientnet_b3(weights=None) # We will load our own weights
    
    # Re-create classifier head
    model.classifier[1] = nn.Linear(model.classifier[1].in_features, NUM_CLASSES)
    
    print(f"Loading weights from {model_path}...")
    try:
        if torch.cuda.is_available():
            state_dict = torch.load(model_path)
        else:
            state_dict = torch.load(model_path, map_location=torch.device('cpu'))
            
        model.load_state_dict(state_dict)
        model = model.to(DEVICE)
        model.eval()
        return model
    except Exception as e:
        print(f"Failed to load model: {e}")
        return None

def evaluate(model, test_loader):
    print("\nStarting evaluation...")
    correct = 0
    total = 0
    
    model.eval()
    with torch.no_grad():
        for i, (imgs, labels, paths) in enumerate(test_loader):
            imgs, labels = imgs.to(DEVICE), labels.to(DEVICE)
            outputs = model(imgs)
            _, preds = torch.max(outputs, 1)
            
            correct += (preds == labels).sum().item()
            total += labels.size(0)
            
            if i % 10 == 0:
                print(f"Processed batch {i}...")

    acc = 100 * correct / total if total > 0 else 0
    print(f"\nEvaluation Complete.")
    print(f"Accuracy: {acc:.2f}% ({correct}/{total})")

def predict_single_image(model, image_path):
    try:
        img = Image.open(image_path).convert('RGB')
        img_tensor = test_transform(img).unsqueeze(0).to(DEVICE)
        
        model.eval()
        with torch.no_grad():
            output = model(img_tensor)
            probs = torch.nn.functional.softmax(output, dim=1)
            _, pred = torch.max(output, 1)
            
        class_idx = pred.item()
        confidence = probs[0][class_idx].item()
        
        print(f"\nImage: {image_path}")
        print(f"Prediction: {CLASS_NAMES[class_idx]} (Confidence: {confidence:.2%})")
        print(f"Probabilities: Underweight: {probs[0][0]:.2f}, Healthy: {probs[0][1]:.2f}, Overweight: {probs[0][2]:.2f}")
        
    except Exception as e:
        print(f"Error predicting image: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Evaluate BCS Model')
    parser.add_argument('--dataset_dir', type=str, help='Path to the root of the cropped dataset (containing dog_dataset1)')
    parser.add_argument('--image', type=str, help='Path to a single image to predict')
    parser.add_argument('--model', type=str, default='bcs_cropped_model.pth', help='Path to the .pth model file')
    parser.add_argument('--info', action='store_true', help='Print model architecture and exit')
    
    args = parser.parse_args()
    
    if not os.path.exists(args.model):
        print(f"Model file not found: {args.model}")
        print("Please ensure the model file is in the current directory or provide the path.")
        exit(1)

    model = load_model(args.model)
    if model is None:
        exit(1)

    if args.info:
        print("\nModel Architecture:")
        print(model)
        print("\nModel loaded successfully.")
        exit(0)

    if args.image:
        predict_single_image(model, args.image)
    elif args.dataset_dir:
        # Reconstruct test set
        # Check if dog_dataset1 is in dataset_dir or if dataset_dir IS dog_dataset1 or parent
        # Notebook used: base_dir = '/content/cropped_bcs_dataset/dog_dataset1'
        
        target_dir = args.dataset_dir
        if os.path.basename(target_dir) != 'dog_dataset1' and os.path.exists(os.path.join(target_dir, 'dog_dataset1')):
             target_dir = os.path.join(target_dir, 'dog_dataset1')
             
        df = load_data_dataframe(target_dir)
        if len(df) == 0:
            print("No images found in dataset.")
            exit(1)
            
        print(f"Total images found: {len(df)}")
        
        # Reproduce split
        # train_test_split logic from notebook
        train_df, test_df = train_test_split(df, test_size=0.2, stratify=df['bcs_label'] if len(df['bcs_label'].unique()) > 1 else None, random_state=42)
        
        print(f"Test set size: {len(test_df)}")
        
        test_dataset = BCSDataset(test_df, transform=test_transform)
        test_loader = DataLoader(test_dataset, batch_size=32, shuffle=False, num_workers=0) # num_workers=0 for windows compat usually better safer
        
        evaluate(model, test_loader)
    else:
        print("\n--- BCS Image Predictor Interactive Mode ---")
        print("Type 'q', 'quit', or 'exit' to stop.")
        while True:
            image_path = input("\nEnter image path (or 'q' to quit): ").strip()
            
            # Handle quit commands
            if image_path.lower() in ['q', 'quit', 'exit']:
                print("Exiting interactive mode.")
                break
            
            if not image_path:
                continue
                
            # Clean path (handle potential quotes if user drags and drops file)
            image_path = image_path.strip('"').strip("'")
            
            if not os.path.exists(image_path):
                print(f"Error: File not found at '{image_path}'")
                continue
            
            if not image_path.lower().endswith(('.jpg', '.jpeg', '.png')):
                print("Warning: File may not be an image. Supported: .jpg, .jpeg, .png")
                
            predict_single_image(model, image_path)
