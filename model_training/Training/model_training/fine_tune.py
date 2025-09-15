import json
import torch
import pandas as pd
from torch.utils.data import Dataset, DataLoader
from transformers import (
    AutoTokenizer, 
    AutoModelForSequenceClassification,
    AutoConfig,
    Trainer,
    TrainingArguments,
    EarlyStoppingCallback
)
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score, classification_report
import numpy as np
import os
from typing import Dict, List
import logging

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DepartmentDataset(Dataset):
    """Dataset class for department recommendation"""
    
    def __init__(self, texts: List[str], labels: List[str], tokenizer, max_length: int = 256):
        self.texts = texts
        self.labels = labels
        self.tokenizer = tokenizer
        self.max_length = max_length
        
        # Label encoding
        self.label_encoder = LabelEncoder()
        self.encoded_labels = self.label_encoder.fit_transform(labels)
        
    def __len__(self):
        return len(self.texts)
    
    def __getitem__(self, idx):
        text = str(self.texts[idx])
        label = self.encoded_labels[idx]
        
        # Tokenize
        encoding = self.tokenizer(
            text,
            truncation=True,
            padding='max_length',
            max_length=self.max_length,
            return_tensors='pt'
        )
        
        return {
            'input_ids': encoding['input_ids'].flatten(),
            'attention_mask': encoding['attention_mask'].flatten(),
            'labels': torch.tensor(label, dtype=torch.long)
        }

class DepartmentRecommendationTrainer:
    """Main trainer class for department recommendation model"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.model_name = config.get('model_name', 'dbmdz/bert-base-turkish-cased')
        self.max_length = config.get('max_length', 256)
        self.batch_size = config.get('batch_size', 16)
        self.learning_rate = config.get('learning_rate', 2e-5)
        self.num_epochs = config.get('num_epochs', 3)
        self.output_dir = config.get('output_dir', '../models/fine_tuned_model')
        
        # Initialize tokenizer
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        
        # Add special tokens if needed
        special_tokens = {'pad_token': '[PAD]'}
        self.tokenizer.add_special_tokens(special_tokens)
        
    def load_training_data(self, train_path: str, val_path: str):
        """Load training and validation data"""
        logger.info(f"Loading training data from {train_path}")
        
        with open(train_path, 'r', encoding='utf-8') as f:
            train_data = json.load(f)
            
        with open(val_path, 'r', encoding='utf-8') as f:
            val_data = json.load(f)
        
        # Extract inputs and outputs
        train_texts = [item['input'] for item in train_data]
        train_labels = [item['output'] for item in train_data]
        
        val_texts = [item['input'] for item in val_data]
        val_labels = [item['output'] for item in val_data]
        
        logger.info(f"Training samples: {len(train_texts)}")
        logger.info(f"Validation samples: {len(val_texts)}")
        logger.info(f"Unique departments: {len(set(train_labels + val_labels))}")
        
        return train_texts, train_labels, val_texts, val_labels
    
    def create_datasets(self, train_texts, train_labels, val_texts, val_labels):
        """Create PyTorch datasets"""
        
        # Create train dataset
        train_dataset = DepartmentDataset(
            texts=train_texts,
            labels=train_labels,
            tokenizer=self.tokenizer,
            max_length=self.max_length
        )
        
        # For validation, use the same label encoder
        val_dataset = DepartmentDataset(
            texts=val_texts,
            labels=val_labels,
            tokenizer=self.tokenizer,
            max_length=self.max_length
        )
        
        # Ensure same label encoding
        val_dataset.label_encoder = train_dataset.label_encoder
        val_dataset.encoded_labels = train_dataset.label_encoder.transform(val_labels)
        
        self.label_encoder = train_dataset.label_encoder
        self.num_labels = len(self.label_encoder.classes_)
        
        logger.info(f"Number of unique labels: {self.num_labels}")
        
        return train_dataset, val_dataset
    
    def load_model(self):
        """Load and configure the model"""
        logger.info(f"Loading model: {self.model_name}")
        
        config = AutoConfig.from_pretrained(
            self.model_name,
            num_labels=self.num_labels,
            finetuning_task="text-classification"
        )
        
        model = AutoModelForSequenceClassification.from_pretrained(
            self.model_name,
            config=config
        )
        
        # Resize token embeddings if special tokens were added
        model.resize_token_embeddings(len(self.tokenizer))
        
        return model
    
    def compute_metrics(self, eval_pred):
        """Compute metrics for evaluation"""
        predictions, labels = eval_pred
        predictions = np.argmax(predictions, axis=1)
        
        accuracy = accuracy_score(labels, predictions)
        
        return {
            'accuracy': accuracy,
            'f1': accuracy  # For now, using accuracy as f1
        }
    
    def train(self, train_dataset, val_dataset):
        """Train the model"""
        logger.info("Starting model training...")
        
        # Load model
        model = self.load_model()
        
        # Training arguments
        training_args = TrainingArguments(
            output_dir=self.output_dir,
            num_train_epochs=self.num_epochs,
            per_device_train_batch_size=self.batch_size,
            per_device_eval_batch_size=self.batch_size,
            warmup_steps=500,
            weight_decay=0.01,
            logging_dir=f'{self.output_dir}/logs',
            logging_steps=100,
            eval_strategy="steps",
            eval_steps=500,
            save_strategy="steps",
            save_steps=1000,
            load_best_model_at_end=True,
            metric_for_best_model="accuracy",
            greater_is_better=True,
            save_total_limit=3,
            dataloader_pin_memory=False,
            fp16=torch.cuda.is_available(),  # Use mixed precision if GPU available
        )
        
        # Initialize trainer
        trainer = Trainer(
            model=model,
            args=training_args,
            train_dataset=train_dataset,
            eval_dataset=val_dataset,
            compute_metrics=self.compute_metrics,
            callbacks=[EarlyStoppingCallback(early_stopping_patience=3)]
        )
        
        # Train
        trainer.train()
        
        # Save final model
        trainer.save_model()
        self.tokenizer.save_pretrained(self.output_dir)
        
        # Save label encoder
        import pickle
        with open(f'{self.output_dir}/label_encoder.pkl', 'wb') as f:
            pickle.dump(self.label_encoder, f)
        
        logger.info(f"Model saved to {self.output_dir}")
        
        return trainer
    
    def evaluate_model(self, trainer, val_dataset):
        """Evaluate the trained model"""
        logger.info("Evaluating model...")
        
        eval_results = trainer.evaluate()
        
        logger.info("Evaluation Results:")
        for key, value in eval_results.items():
            logger.info(f"{key}: {value}")
        
        return eval_results
    
    def test_model_predictions(self, trainer, test_inputs: List[str], num_predictions: int = 5):
        """Test model with sample inputs"""
        logger.info(f"Testing model with {len(test_inputs)} sample inputs...")
        
        model = trainer.model
        model.eval()
        
        with torch.no_grad():
            for i, text in enumerate(test_inputs[:num_predictions]):
                # Tokenize
                inputs = self.tokenizer(
                    text,
                    truncation=True,
                    padding='max_length',
                    max_length=self.max_length,
                    return_tensors='pt'
                )
                
                # Predict
                outputs = model(**inputs)
                predictions = torch.nn.functional.softmax(outputs.logits, dim=-1)
                predicted_class_id = predictions.argmax().item()
                confidence = predictions.max().item()
                
                # Decode prediction
                predicted_department = self.label_encoder.inverse_transform([predicted_class_id])[0]
                
                logger.info(f"\nTest {i+1}:")
                logger.info(f"Input: {text}")
                logger.info(f"Prediction: {predicted_department}")
                logger.info(f"Confidence: {confidence:.4f}")

def main():
    """Main training function"""
    
    # Configuration
    config = {
        'model_name': 'dbmdz/bert-base-turkish-cased',
        'max_length': 256,
        'batch_size': 8,  # Reduced for memory efficiency
        'learning_rate': 2e-5,
        'num_epochs': 3,
        'output_dir': '../models/department_recommendation_model'
    }
    
    # Initialize trainer
    trainer = DepartmentRecommendationTrainer(config)
    
    # Load data
    train_texts, train_labels, val_texts, val_labels = trainer.load_training_data(
        '/Users/ardaerdegirmenci/Desktop/Pupilica/giverny/model_training/model_datasets/train_data.json',
        '/Users/ardaerdegirmenci/Desktop/Pupilica/giverny/model_training/model_datasets/val_data.json'
    )
    
    # Create datasets
    train_dataset, val_dataset = trainer.create_datasets(
        train_texts, train_labels, val_texts, val_labels
    )
    
    # Train model
    trained_model = trainer.train(train_dataset, val_dataset)
    
    # Evaluate
    eval_results = trainer.evaluate_model(trained_model, val_dataset)
    
    # Test with sample inputs
    test_inputs = [
        "İlgi alanlarım: teknoloji, matematik. YKS sıralaması: 200000",
        "İlgi alanlarım: sağlık, hasta bakımı. YKS sıralaması: 400000",
        "İlgi alanlarım: sanat, tasarım. YKS sıralaması: 600000"
    ]
    
    trainer.test_model_predictions(trained_model, test_inputs)
    
    logger.info("Training completed successfully!")

if __name__ == "__main__":
    main()